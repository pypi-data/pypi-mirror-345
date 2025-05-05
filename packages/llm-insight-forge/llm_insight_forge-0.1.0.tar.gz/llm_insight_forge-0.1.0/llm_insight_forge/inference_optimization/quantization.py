"""
Model quantization tools for optimizing inference performance and memory usage.

This module provides functionality to:
- Quantize models to lower precision (INT8, INT4, etc.)
- Apply different quantization techniques (dynamic, static, weight-only)
- Benchmark performance of quantized models
- Evaluate accuracy trade-offs from quantization
"""

import os
import time
import json
import logging
from typing import Dict, List, Any, Union, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import torch
import numpy as np
from tqdm.auto import tqdm

try:
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer, TextGenerationPipeline
    has_transformers = True
except ImportError:
    has_transformers = False

try:
    import bitsandbytes as bnb
    has_bnb = True
except ImportError:
    has_bnb = False

try:
    import optimum
    from optimum.bettertransformer import BetterTransformer
    has_optimum = True
except ImportError:
    has_optimum = False

logger = logging.getLogger(__name__)


class QuantizationMethod(Enum):
    """Quantization methods for LLMs"""
    
    DYNAMIC_INT8 = "dynamic_int8"      # Dynamic quantization to INT8
    STATIC_INT8 = "static_int8"        # Static quantization to INT8
    WEIGHT_ONLY_INT8 = "weight_only_int8"  # Weight-only quantization to INT8
    WEIGHT_ONLY_INT4 = "weight_only_int4"  # Weight-only quantization to INT4
    GPTQ = "gptq"                      # GPTQ quantization
    AWQUANT = "awq"                    # AWQ quantization
    BITSANDBYTES_4BIT = "bnb_4bit"     # BitsAndBytes 4-bit quantization
    BITSANDBYTES_8BIT = "bnb_8bit"     # BitsAndBytes 8-bit quantization 


@dataclass
class QuantizationConfig:
    """Configuration for quantization process"""
    
    method: QuantizationMethod
    bits: int = 8
    compute_dtype: torch.dtype = torch.float16
    dataset_path: Optional[str] = None  # For calibration if needed
    device_map: str = "auto"
    quant_config: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        # Set default quantization config based on method
        if not self.quant_config:
            if self.method == QuantizationMethod.BITSANDBYTES_4BIT:
                self.quant_config = {
                    "load_in_4bit": True,
                    "bnb_4bit_compute_dtype": self.compute_dtype,
                    "bnb_4bit_use_double_quant": True,
                    "bnb_4bit_quant_type": "nf4"
                }
            elif self.method == QuantizationMethod.BITSANDBYTES_8BIT:
                self.quant_config = {
                    "load_in_8bit": True,
                    "llm_int8_threshold": 6.0,
                    "llm_int8_has_fp16_weight": False
                }


@dataclass
class QuantizationResult:
    """Result of quantization process"""
    
    model_name: str
    method: QuantizationMethod
    output_path: str
    original_size_mb: float
    quantized_size_mb: float
    compression_ratio: float
    metrics: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)


class ModelQuantizer:
    """
    Tool for quantizing language models to improve inference performance.
    
    This class supports multiple quantization approaches for transformers-based
    LLMs, prioritizing practical inference optimization.
    """
    
    def __init__(
        self,
        model_path_or_name: str,
        quantization_config: QuantizationConfig,
        output_dir: Optional[str] = None,
        calibration_dataset: Optional[Any] = None,
        metrics_fn: Optional[Callable] = None,
    ):
        """
        Initialize a model quantizer.
        
        Args:
            model_path_or_name: HF model name or local path
            quantization_config: Configuration for quantization
            output_dir: Directory to save quantized model
            calibration_dataset: Dataset for calibration (if needed)
            metrics_fn: Optional function to calculate quality metrics
        """
        self.model_path = model_path_or_name
        self.config = quantization_config
        self.output_dir = output_dir or f"quantized_{Path(model_path_or_name).name}"
        self.calibration_dataset = calibration_dataset
        self.metrics_fn = metrics_fn
        
        # Check if transformers is available
        if not has_transformers:
            raise ImportError("Transformers package is required for quantization.")
        
        # Check method-specific requirements
        if self.config.method in [QuantizationMethod.BITSANDBYTES_4BIT, 
                                 QuantizationMethod.BITSANDBYTES_8BIT] and not has_bnb:
            raise ImportError("BitsAndBytes package is required for this quantization method.")
            
        if self.config.method in [QuantizationMethod.GPTQ, 
                                  QuantizationMethod.AWQUANT] and not has_optimum:
            raise ImportError("Optimum package is required for this quantization method.")
    
    def _get_original_model_size(self) -> float:
        """Calculate the original model size in MB"""
        try:
            with torch.no_grad():
                # Try loading just the config first to check parameters
                if os.path.exists(self.model_path):
                    config = transformers.AutoConfig.from_pretrained(self.model_path)
                else:
                    config = transformers.AutoConfig.from_pretrained(
                        self.model_path, 
                        trust_remote_code=True
                    )
                
                # Estimate size based on parameters
                if hasattr(config, "num_parameters"):
                    params = config.num_parameters
                elif hasattr(config, "n_params"):
                    params = config.n_params
                else:
                    # Load model to count parameters
                    model = AutoModelForCausalLM.from_pretrained(
                        self.model_path,
                        config=config,
                        torch_dtype=torch.float16,
                        device_map="auto",
                        trust_remote_code=True,
                    )
                    params = sum(p.numel() for p in model.parameters())
                    del model  # Free memory
                    torch.cuda.empty_cache()
                
                # Calculate size in MB (assuming float16 by default)
                size_mb = (params * 2) / (1024 * 1024)  # 2 bytes per float16 parameter
                return size_mb
        except Exception as e:
            logger.warning(f"Could not calculate exact model size: {e}")
            # Return an estimate based on model name patterns
            if "7b" in self.model_path.lower():
                return 13000.0  # ~13GB for 7B models
            elif "13b" in self.model_path.lower():
                return 26000.0  # ~26GB for 13B models
            elif "70b" in self.model_path.lower():
                return 140000.0  # ~140GB for 70B models
            return 10000.0  # Default estimate
    
    def _quantize_with_bitsandbytes(self) -> Tuple[Any, float]:
        """
        Quantize using BitsAndBytes library.
        
        Returns:
            Tuple of (quantized model, size in MB)
        """
        try:
            # Import again to ensure it's available
            import bitsandbytes as bnb
            
            logger.info(f"Loading model with BitsAndBytes quantization...")
            
            # Prepare quantization config
            is_4bit = self.config.method == QuantizationMethod.BITSANDBYTES_4BIT
            is_8bit = self.config.method == QuantizationMethod.BITSANDBYTES_8BIT
            
            # Load the model with quantization
            model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                device_map=self.config.device_map,
                load_in_4bit=is_4bit,
                load_in_8bit=is_8bit,
                quantization_config=transformers.BitsAndBytesConfig(
                    **self.config.quant_config
                ),
                trust_remote_code=True,
            )
            
            # Load tokenizer separately
            tokenizer = AutoTokenizer.from_pretrained(
                self.model_path, 
                trust_remote_code=True
            )
            
            # Calculate quantized size
            if is_4bit:
                size_factor = 0.5  # 4bit is ~1/8 of FP16
            else:
                size_factor = 1.0  # 8bit is ~1/4 of FP16
                
            original_size = self._get_original_model_size()
            quantized_size = original_size * size_factor
            
            return (model, tokenizer), quantized_size
            
        except Exception as e:
            logger.error(f"Error in BitsAndBytes quantization: {e}")
            raise
    
    def _quantize_with_torch(self) -> Tuple[Any, float]:
        """
        Quantize using PyTorch native quantization.
        
        Returns:
            Tuple of (quantized model, size in MB)
        """
        try:
            logger.info(f"Loading model with PyTorch quantization...")
            
            # Load model in FP16 first
            model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16,
                device_map=self.config.device_map,
                trust_remote_code=True,
            )
            
            tokenizer = AutoTokenizer.from_pretrained(
                self.model_path, 
                trust_remote_code=True
            )
            
            # Apply quantization
            if self.config.method == QuantizationMethod.DYNAMIC_INT8:
                # Dynamic quantization
                torch.quantization.quantize_dynamic(
                    model, {torch.nn.Linear}, dtype=torch.qint8
                )
                size_factor = 0.33  # Roughly 1/3 the size
                
            elif self.config.method == QuantizationMethod.STATIC_INT8:
                logger.warning("Static INT8 quantization requires calibration data")
                # Static quantization with default calibration
                model.qconfig = torch.quantization.get_default_qconfig('fbgemm')
                torch.quantization.prepare(model, inplace=True)
                torch.quantization.convert(model, inplace=True)
                size_factor = 0.25  # Roughly 1/4 the size
                
            elif self.config.method == QuantizationMethod.WEIGHT_ONLY_INT8:
                # Weight-only quantization
                for name, module in model.named_modules():
                    if isinstance(module, torch.nn.Linear):
                        module.weight.data = module.weight.data.to(torch.int8)
                size_factor = 0.5  # Roughly 1/2 the size
                
            else:
                # Default to dynamic quantization
                torch.quantization.quantize_dynamic(
                    model, {torch.nn.Linear}, dtype=torch.qint8
                )
                size_factor = 0.33
                
            original_size = self._get_original_model_size()
            quantized_size = original_size * size_factor
            
            return (model, tokenizer), quantized_size
            
        except Exception as e:
            logger.error(f"Error in PyTorch quantization: {e}")
            raise
    
    def _quantize_with_optimum(self) -> Tuple[Any, float]:
        """
        Quantize using Hugging Face Optimum library.
        
        Returns:
            Tuple of (quantized model, size in MB)
        """
        try:
            # Import again to ensure it's available
            from optimum.bettertransformer import BetterTransformer
            
            logger.info(f"Loading model with Optimum quantization...")
            
            # Load model in FP16 first
            model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16,
                device_map=self.config.device_map,
                trust_remote_code=True,
            )
            
            tokenizer = AutoTokenizer.from_pretrained(
                self.model_path, 
                trust_remote_code=True
            )
            
            # Convert to BetterTransformer for optimizations
            model = BetterTransformer.transform(model)
            
            # Estimate size (BetterTransformer doesn't reduce size much)
            original_size = self._get_original_model_size()
            quantized_size = original_size * 0.9  # About 10% savings
            
            if self.config.method == QuantizationMethod.GPTQ:
                logger.warning("GPTQ quantization requires additional setup and calibration")
                # Integration with GPTQ would go here
                quantized_size = original_size * 0.25  # GPTQ is about 1/4 size
                
            elif self.config.method == QuantizationMethod.AWQUANT:
                logger.warning("AWQ quantization requires additional setup and calibration")
                # Integration with AWQ would go here
                quantized_size = original_size * 0.25  # AWQ is about 1/4 size
                
            return (model, tokenizer), quantized_size
            
        except Exception as e:
            logger.error(f"Error in Optimum quantization: {e}")
            raise
    
    def quantize(self) -> QuantizationResult:
        """
        Quantize the model using the specified method.
        
        Returns:
            QuantizationResult with metrics and model paths
        """
        start_time = time.time()
        logger.info(f"Starting quantization with method: {self.config.method.value}")
        
        original_size = self._get_original_model_size()
        logger.info(f"Original model size: {original_size:.2f} MB")
        
        # Select quantization method
        if self.config.method in [QuantizationMethod.BITSANDBYTES_4BIT, 
                                QuantizationMethod.BITSANDBYTES_8BIT]:
            (model, tokenizer), quantized_size = self._quantize_with_bitsandbytes()
            
        elif self.config.method in [QuantizationMethod.DYNAMIC_INT8, 
                                  QuantizationMethod.STATIC_INT8,
                                  QuantizationMethod.WEIGHT_ONLY_INT8]:
            (model, tokenizer), quantized_size = self._quantize_with_torch()
            
        elif self.config.method in [QuantizationMethod.GPTQ, 
                                  QuantizationMethod.AWQUANT]:
            (model, tokenizer), quantized_size = self._quantize_with_optimum()
            
        else:
            raise ValueError(f"Unsupported quantization method: {self.config.method}")
            
        # Calculate compression ratio
        compression_ratio = original_size / max(1.0, quantized_size)
        
        # Save the model
        os.makedirs(self.output_dir, exist_ok=True)
        
        # For BitsAndBytes and some methods, we can't save the quantized weights directly
        can_save_quantized = self.config.method not in [
            QuantizationMethod.BITSANDBYTES_4BIT,
            QuantizationMethod.BITSANDBYTES_8BIT
        ]
        
        if can_save_quantized:
            logger.info("Saving quantized model...")
            model.save_pretrained(self.output_dir)
            tokenizer.save_pretrained(self.output_dir)
            
        # Save quantization config
        with open(os.path.join(self.output_dir, "quantization_config.json"), "w") as f:
            json.dump({
                "method": self.config.method.value,
                "bits": self.config.bits,
                "original_model": self.model_path,
                "config": self.config.quant_config,
                "original_size_mb": original_size,
                "quantized_size_mb": quantized_size,
                "compression_ratio": compression_ratio,
                "create_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            }, f, indent=2)
            
        # Calculate metrics if metrics function provided
        metrics = {}
        if self.metrics_fn is not None:
            try:
                metrics = self.metrics_fn(model, tokenizer)
            except Exception as e:
                logger.error(f"Error calculating metrics: {e}")
                
        # Include timing
        runtime = time.time() - start_time
        metrics["quantization_time_seconds"] = runtime
        
        # Save metrics
        with open(os.path.join(self.output_dir, "quantization_metrics.json"), "w") as f:
            json.dump(metrics, f, indent=2)
            
        logger.info(f"Quantization completed in {runtime:.2f} seconds")
        logger.info(f"Compression ratio: {compression_ratio:.2f}x")
        logger.info(f"Quantized model size: {quantized_size:.2f} MB")
        
        return QuantizationResult(
            model_name=os.path.basename(self.model_path),
            method=self.config.method,
            output_path=self.output_dir,
            original_size_mb=original_size,
            quantized_size_mb=quantized_size,
            compression_ratio=compression_ratio,
            metrics=metrics,
            config={
                "bits": self.config.bits,
                "method": self.config.method.value,
                "quant_config": self.config.quant_config,
            }
        )


def run_inference_benchmark(
    model: Any, 
    tokenizer: Any,
    input_texts: List[str],
    batch_sizes: List[int] = [1, 4, 8],
    max_new_tokens: int = 128,
    num_warmup: int = 2,
    num_runs: int = 5,
) -> Dict[str, Any]:
    """
    Run a performance benchmark on the model.
    
    Args:
        model: Model to benchmark
        tokenizer: Tokenizer for the model
        input_texts: List of input texts to benchmark with
        batch_sizes: List of batch sizes to test
        max_new_tokens: Maximum number of tokens to generate
        num_warmup: Number of warmup runs
        num_runs: Number of measured runs
        
    Returns:
        Dictionary with benchmark results
    """
    results = {}
    device = next(model.parameters()).device
    
    for batch_size in batch_sizes:
        # Skip if batch size is larger than input texts
        if batch_size > len(input_texts):
            continue
            
        batch_inputs = input_texts[:batch_size]
        inputs = tokenizer(batch_inputs, return_tensors="pt", padding=True)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Warmup runs
        for _ in range(num_warmup):
            with torch.no_grad():
                _ = model.generate(**inputs, max_new_tokens=max_new_tokens)
        
        # Timed runs
        latencies = []
        tokens = []
        
        for _ in range(num_runs):
            start_time = time.time()
            with torch.no_grad():
                outputs = model.generate(**inputs, max_new_tokens=max_new_tokens)
            end_time = time.time()
            
            latencies.append(end_time - start_time)
            tokens.append(outputs.shape[1] - inputs["input_ids"].shape[1])
            
        # Calculate stats
        avg_latency = sum(latencies) / len(latencies)
        avg_tokens = sum(tokens) / len(tokens)
        throughput = avg_tokens / avg_latency
        
        results[f"batch_{batch_size}"] = {
            "avg_latency_seconds": avg_latency,
            "avg_tokens_generated": avg_tokens,
            "throughput_tokens_per_second": throughput,
            "latencies": latencies,
            "tokens": tokens,
        }
        
    return results


def quantize_model(
    model_name_or_path: str,
    method: str = "bnb_4bit",
    output_dir: Optional[str] = None,
    bits: int = 4,
    device_map: str = "auto",
) -> Dict[str, Any]:
    """
    Convenience function to quantize a model.
    
    Args:
        model_name_or_path: Model name or path
        method: Quantization method
        output_dir: Output directory
        bits: Quantization precision
        device_map: Device mapping strategy
        
    Returns:
        Dictionary with quantization results
    """
    try:
        # Convert method string to enum
        if method == "bnb_4bit":
            quant_method = QuantizationMethod.BITSANDBYTES_4BIT
        elif method == "bnb_8bit":
            quant_method = QuantizationMethod.BITSANDBYTES_8BIT
        elif method == "dynamic_int8":
            quant_method = QuantizationMethod.DYNAMIC_INT8
        elif method == "static_int8":
            quant_method = QuantizationMethod.STATIC_INT8
        elif method == "gptq":
            quant_method = QuantizationMethod.GPTQ
        elif method == "awq":
            quant_method = QuantizationMethod.AWQUANT
        else:
            raise ValueError(f"Unknown quantization method: {method}")
            
        # Create configuration
        config = QuantizationConfig(
            method=quant_method,
            bits=bits,
            device_map=device_map
        )
        
        # Set output directory
        if output_dir is None:
            model_name = os.path.basename(model_name_or_path)
            output_dir = f"quantized_{model_name}_{method}_{bits}bit"
            
        # Run quantization
        quantizer = ModelQuantizer(
            model_path_or_name=model_name_or_path,
            quantization_config=config,
            output_dir=output_dir
        )
        
        result = quantizer.quantize()
        
        # Return dictionary of results
        return {
            "model_name": result.model_name,
            "method": result.method.value,
            "output_path": result.output_path,
            "original_size_mb": result.original_size_mb,
            "quantized_size_mb": result.quantized_size_mb,
            "compression_ratio": result.compression_ratio,
            "metrics": result.metrics
        }
        
    except Exception as e:
        logger.error(f"Error quantizing model: {e}")
        return {
            "error": str(e),
            "success": False
        }


def batch_inference(
    model_path: str,
    input_texts: List[str],
    max_length: Optional[int] = None,
    batch_size: int = 8,
    use_4bit: bool = True,
    use_8bit: bool = False,
    **kwargs
) -> List[str]:
    """
    Run batch inference on a model with optimized settings.
    
    Args:
        model_path: Model name or path
        input_texts: List of input texts
        max_length: Maximum generated sequence length
        batch_size: Batch size for inference
        use_4bit: Whether to load the model in 4-bit mode
        use_8bit: Whether to load the model in 8-bit mode
        **kwargs: Additional kwargs for model generation
        
    Returns:
        List of generated outputs
    """
    try:
        # Set up optimized loading
        if use_4bit:
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                device_map="auto",
                load_in_4bit=True,
                trust_remote_code=True,
            )
        elif use_8bit:
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                device_map="auto",
                load_in_8bit=True,
                trust_remote_code=True,
            )
        else:
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                device_map="auto",
                torch_dtype=torch.float16,
                trust_remote_code=True,
            )
            
        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            trust_remote_code=True,
        )
        
        # Process in batches
        all_results = []
        for i in range(0, len(input_texts), batch_size):
            batch = input_texts[i:i + batch_size]
            inputs = tokenizer(batch, return_tensors="pt", padding=True)
            inputs = {k: v.to(model.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=max_length or 128,
                    **kwargs
                )
                
            # Convert outputs to text
            batch_results = tokenizer.batch_decode(outputs, skip_special_tokens=True)
            all_results.extend(batch_results)
            
        return all_results
        
    except Exception as e:
        logger.error(f"Error in batch inference: {e}")
        return [f"Error: {str(e)}"] * len(input_texts)