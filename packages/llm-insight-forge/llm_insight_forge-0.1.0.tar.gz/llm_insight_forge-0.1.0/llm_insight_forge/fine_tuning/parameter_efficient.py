"""
Parameter-Efficient Fine-Tuning (PEFT) methods for LLMs.

This module provides implementations of PEFT techniques such as:
- LoRA (Low-Rank Adaptation)
- QLoRA (Quantized Low-Rank Adaptation)
- Adapters
- Prefix tuning
- Prompt tuning

These methods allow fine-tuning large models with much lower computational resources
by updating only a small number of parameters.
"""

import os
import time
from typing import Dict, List, Any, Union, Optional, Tuple
from dataclasses import dataclass, field
import logging
from pathlib import Path

import torch
import numpy as np
from transformers import (
    TrainingArguments,
    Trainer,
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    BitsAndBytesConfig
)
from peft import (
    get_peft_model,
    LoraConfig,
    TaskType,
    PrefixTuningConfig,
    PromptTuningConfig,
    PromptTuningInit,
    # AdapterConfig is not available in the current PEFT version
    PeftConfig as PeftConfigBase
)
from datasets import Dataset, DatasetDict

logger = logging.getLogger(__name__)


# Add the missing functions
def create_lora_config(
    r: int = 8,
    lora_alpha: int = 16,
    lora_dropout: float = 0.05,
    bias: str = "none",
    task_type: str = "CAUSAL_LM",
    target_modules: Optional[List[str]] = None,
) -> LoraConfig:
    """
    Create a LoRA configuration object.
    
    Args:
        r: Rank of the update matrices
        lora_alpha: Alpha parameter for LoRA scaling
        lora_dropout: Dropout probability for LoRA layers
        bias: Bias type, one of 'none', 'all', or 'lora_only'
        task_type: Task type for LoRA
        target_modules: List of module names to apply LoRA to
        
    Returns:
        LoraConfig object
    """
    task_type_enum = TaskType.CAUSAL_LM if task_type == "CAUSAL_LM" else TaskType.SEQ_2_SEQ_LM
    
    return LoraConfig(
        r=r,
        lora_alpha=lora_alpha,
        lora_dropout=lora_dropout,
        bias=bias,
        task_type=task_type_enum,
        target_modules=target_modules,
    )


def create_qlora_config(
    r: int = 8,
    lora_alpha: int = 16,
    lora_dropout: float = 0.05,
    bias: str = "none",
    task_type: str = "CAUSAL_LM",
    target_modules: Optional[List[str]] = None,
    bits: int = 4,
    quant_type: str = "nf4",
) -> Dict[str, Any]:
    """
    Create a QLoRA configuration dictionary.
    
    This creates both a LoRA config and a BitsAndBytes quantization config.
    
    Args:
        r: Rank of the update matrices
        lora_alpha: Alpha parameter for LoRA scaling
        lora_dropout: Dropout probability for LoRA layers
        bias: Bias type, one of 'none', 'all', or 'lora_only'
        task_type: Task type for LoRA
        target_modules: List of module names to apply LoRA to
        bits: Bits for quantization (4 or 8)
        quant_type: Quantization type (nf4, fp4)
        
    Returns:
        Dictionary containing both lora_config and quantization_config
    """
    # Create LoRA config
    lora_config = create_lora_config(
        r=r,
        lora_alpha=lora_alpha,
        lora_dropout=lora_dropout,
        bias=bias,
        task_type=task_type,
        target_modules=target_modules,
    )
    
    # Create BitsAndBytes config
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=(bits == 4),
        load_in_8bit=(bits == 8),
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_quant_type=quant_type,
        bnb_4bit_use_double_quant=True,
    )
    
    return {
        "lora_config": lora_config,
        "quantization_config": bnb_config,
    }


def create_adapter_config(
    dim: int = 128,
    hidden_dim: Optional[int] = None,
    task_type: str = "CAUSAL_LM",
    scaling: float = 1.0,
    adapter_dropout: float = 0.0,
    target_modules: Optional[List[str]] = None,
) -> PeftConfigBase:
    """
    Create an Adapter configuration object.
    
    Note: Using LoraConfig as a fallback since AdapterConfig is not available
    in the current installed version of PEFT.
    
    Args:
        dim: Dimension of adapter layers
        hidden_dim: Dimension of the hidden layers (if None, 4x dim is used)
        task_type: Task type for the adapter
        scaling: Adapter scaling factor
        adapter_dropout: Dropout rate for adapter layers
        target_modules: Which modules to apply the adapter to
        
    Returns:
        A PEFT configuration object suitable for adapters
    """
    task_type_enum = TaskType.CAUSAL_LM if task_type == "CAUSAL_LM" else TaskType.SEQ_2_SEQ_LM
    
    if hidden_dim is None:
        hidden_dim = 4 * dim
    
    # Since AdapterConfig might not be available in this PEFT version,
    # we'll use LoraConfig as a fallback
    logger.warning(
        "AdapterConfig is not available in your PEFT version. "
        "Using LoraConfig as a fallback. Consider upgrading PEFT."
    )
    
    return LoraConfig(
        r=dim,  # Use dim as rank
        lora_alpha=scaling,
        lora_dropout=adapter_dropout,
        target_modules=target_modules,
        task_type=task_type_enum,
    )


def create_peft_model(model, peft_config) -> Any:
    """
    Create a PEFT model by applying a PEFT configuration to a base model.
    
    Args:
        model: Base model to apply PEFT to
        peft_config: PEFT configuration object (e.g., LoraConfig)
        
    Returns:
        PEFT model
    """
    peft_model = get_peft_model(model, peft_config)
    
    # Log trainable parameters
    total_params = sum(p.numel() for p in peft_model.parameters())
    trainable_params = sum(p.numel() for p in peft_model.parameters() if p.requires_grad)
    logger.info(f"Total parameters: {total_params:,}")
    logger.info(f"Trainable parameters: {trainable_params:,} ({trainable_params/total_params:.2%})")
    
    return peft_model


@dataclass
class PeftConfig:
    """Configuration for parameter-efficient fine-tuning"""
    
    peft_method: str = "lora"  # "lora", "qlora", "prefix", "prompt", "adapter"
    
    # LoRA specific settings
    lora_r: int = 8  # Rank of the update matrices
    lora_alpha: int = 16  # Alpha parameter for LoRA scaling
    lora_dropout: float = 0.05  # Dropout probability for LoRA layers
    lora_target_modules: Optional[List[str]] = None  # Which modules to apply LoRA to
    
    # QLoRA specific settings
    quantization_bits: int = 4  # Bits for quantization (4 or 8)
    quantization_type: str = "nf4"  # Quantization type (nf4, fp4, int8)
    
    # Prefix tuning specific settings
    num_virtual_tokens: int = 20  # Number of virtual tokens for prefix tuning
    
    # Training settings
    learning_rate: float = 5e-5
    num_train_epochs: int = 3
    max_steps: int = -1  # Override epochs (-1 means use epochs instead)
    per_device_train_batch_size: int = 4
    gradient_accumulation_steps: int = 1
    weight_decay: float = 0.01
    warmup_ratio: float = 0.1
    lr_scheduler_type: str = "cosine"
    logging_steps: int = 10
    save_steps: int = 100
    eval_steps: int = 100
    output_dir: str = "./output"
    fp16: bool = False
    bf16: bool = False
    
    # Data settings
    max_length: int = 512


class ParameterEfficientFineTuner:
    """
    Fine-tuner for parameter-efficient methods like LoRA and QLoRA.
    
    This class provides methods for fine-tuning large language models with
    minimal computational resources by updating only a small subset of parameters.
    """
    
    def __init__(
        self,
        base_model_name_or_path: str,
        config: Optional[PeftConfig] = None,
        tokenizer=None,
    ):
        """
        Initialize the fine-tuner.
        
        Args:
            base_model_name_or_path: Name or path of the base model
            config: Configuration for parameter-efficient fine-tuning
            tokenizer: Optional pre-loaded tokenizer
        """
        self.base_model_name_or_path = base_model_name_or_path
        self.config = config or PeftConfig()
        self.tokenizer = tokenizer
        self.model = None
        self.peft_config = None
    
    def prepare_model(self) -> None:
        """
        Prepare the model for parameter-efficient fine-tuning.
        
        This method loads the base model and applies the PEFT configuration.
        """
        try:
            # Load tokenizer if not provided
            if self.tokenizer is None:
                self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_name_or_path)
                # Ensure the tokenizer has a pad token
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Set up quantization for QLoRA
            if self.config.peft_method == "qlora":
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=self.config.quantization_bits == 4,
                    load_in_8bit=self.config.quantization_bits == 8,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_quant_type=self.config.quantization_type,
                )
                
                # Load model with quantization
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.base_model_name_or_path,
                    quantization_config=bnb_config,
                    device_map="auto",
                    torch_dtype=torch.float16,
                )
            else:
                # Load model normally
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.base_model_name_or_path,
                    device_map="auto",
                    torch_dtype=torch.float16 if self.config.fp16 else None,
                )
            
            # Configure PEFT method
            if self.config.peft_method in ["lora", "qlora"]:
                # Determine target modules if not specified
                if self.config.lora_target_modules is None:
                    # Default target modules based on model architecture
                    model_type = self.model.config.model_type.lower()
                    if "llama" in model_type:
                        self.config.lora_target_modules = ["q_proj", "k_proj", "v_proj", "o_proj"]
                    elif "mistral" in model_type:
                        self.config.lora_target_modules = ["q_proj", "k_proj", "v_proj", "o_proj"]
                    elif "gpt" in model_type:
                        self.config.lora_target_modules = ["c_attn", "c_proj"]
                    else:
                        # Generic default
                        self.config.lora_target_modules = ["query", "key", "value", "output"]
                
                self.peft_config = LoraConfig(
                    r=self.config.lora_r,
                    lora_alpha=self.config.lora_alpha,
                    lora_dropout=self.config.lora_dropout,
                    target_modules=self.config.lora_target_modules,
                    bias="none",
                    task_type=TaskType.CAUSAL_LM,
                )
                
            elif self.config.peft_method == "prefix":
                self.peft_config = PrefixTuningConfig(
                    task_type=TaskType.CAUSAL_LM,
                    num_virtual_tokens=self.config.num_virtual_tokens,
                )
                
            elif self.config.peft_method == "prompt":
                self.peft_config = PromptTuningConfig(
                    task_type=TaskType.CAUSAL_LM,
                    prompt_tuning_init=PromptTuningInit.TEXT,
                    num_virtual_tokens=self.config.num_virtual_tokens,
                    tokenizer_name_or_path=self.base_model_name_or_path,
                )
                
            else:
                raise ValueError(f"Unsupported PEFT method: {self.config.peft_method}")
            
            # Apply PEFT configuration
            if self.peft_config is not None:
                self.model = get_peft_model(self.model, self.peft_config)
                self.model.print_trainable_parameters()
                
        except Exception as e:
            logger.error(f"Error preparing model: {e}")
            raise
    
    def _prepare_dataset(
        self, 
        dataset: Union[Dataset, DatasetDict],
        text_column: str = "formatted_text"
    ) -> Dict[str, Dataset]:
        """
        Prepare dataset for fine-tuning.
        
        Args:
            dataset: Input dataset
            text_column: Column containing the text to use for fine-tuning
            
        Returns:
            Dictionary mapping split names to tokenized datasets
        """
        # Extract splits
        train_dataset = None
        eval_dataset = None
        
        if isinstance(dataset, DatasetDict):
            # Use existing splits
            if "train" in dataset:
                train_dataset = dataset["train"]
            if "validation" in dataset or "test" in dataset:
                eval_dataset = dataset.get("validation", dataset.get("test"))
        else:
            # Use single dataset as training data
            train_dataset = dataset
        
        if train_dataset is None:
            raise ValueError("No training data found in the dataset")
            
        # Function to tokenize text
        def tokenize_function(examples):
            texts = examples[text_column]
            
            if not isinstance(texts, list):
                texts = [texts]
                
            # Tokenize inputs
            tokenized = self.tokenizer(
                texts,
                truncation=True,
                max_length=self.config.max_length,
                padding="max_length",
                return_tensors="pt",
            )
            
            # Set labels equal to input_ids for causal LM training
            tokenized["labels"] = tokenized["input_ids"].clone()
            
            return tokenized
        
        # Apply tokenization
        tokenized_train = train_dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=[col for col in train_dataset.column_names 
                           if col != text_column]
        )
        
        tokenized_eval = None
        if eval_dataset is not None:
            tokenized_eval = eval_dataset.map(
                tokenize_function,
                batched=True,
                remove_columns=[col for col in eval_dataset.column_names 
                               if col != text_column]
            )
            
        result = {"train": tokenized_train}
        if tokenized_eval is not None:
            result["eval"] = tokenized_eval
            
        return result
    
    def train(
        self,
        dataset: Union[Dataset, DatasetDict],
        text_column: str = "formatted_text",
        output_dir: Optional[str] = None,
        resume_from_checkpoint: Optional[str] = None,
    ) -> Tuple[Any, Dict[str, float]]:
        """
        Train the model with parameter-efficient fine-tuning.
        
        Args:
            dataset: Training dataset
            text_column: Column containing the text to use for training
            output_dir: Directory to save the model checkpoints
            resume_from_checkpoint: Path to a checkpoint to resume training from
            
        Returns:
            Tuple of (trained model, evaluation metrics)
        """
        # Prepare model if not already prepared
        if self.model is None:
            self.prepare_model()
        
        # Prepare dataset
        try:
            tokenized_datasets = self._prepare_dataset(dataset, text_column)
        except Exception as e:
            logger.error(f"Error preparing dataset: {e}")
            raise
            
        # Set up training arguments
        output_dir = output_dir or self.config.output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        training_args = TrainingArguments(
            output_dir=output_dir,
            learning_rate=self.config.learning_rate,
            num_train_epochs=self.config.num_train_epochs,
            max_steps=self.config.max_steps,
            per_device_train_batch_size=self.config.per_device_train_batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            weight_decay=self.config.weight_decay,
            warmup_ratio=self.config.warmup_ratio,
            lr_scheduler_type=self.config.lr_scheduler_type,
            logging_steps=self.config.logging_steps,
            save_steps=self.config.save_steps,
            evaluation_strategy="steps" if "eval" in tokenized_datasets else "no",
            eval_steps=self.config.eval_steps if "eval" in tokenized_datasets else None,
            load_best_model_at_end=True if "eval" in tokenized_datasets else False,
            fp16=self.config.fp16,
            bf16=self.config.bf16,
            report_to="tensorboard",
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,  # Causal language modeling, not masked language modeling
        )
        
        # Initialize Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_datasets["train"],
            eval_dataset=tokenized_datasets.get("eval"),
            data_collator=data_collator,
            tokenizer=self.tokenizer,
        )
        
        # Train the model
        trainer.train(resume_from_checkpoint=resume_from_checkpoint)
        
        # Save the final model
        model_save_path = os.path.join(output_dir, "final_model")
        self.model.save_pretrained(model_save_path)
        self.tokenizer.save_pretrained(model_save_path)
        
        # Evaluate the model
        eval_results = {}
        if "eval" in tokenized_datasets:
            logger.info("Evaluating the model...")
            eval_results = trainer.evaluate()
        
        return self.model, eval_results
    
    def save_model(
        self, 
        save_dir: str, 
        save_tokenizer: bool = True,
        merge_adapter: bool = False
    ) -> str:
        """
        Save the fine-tuned model.
        
        Args:
            save_dir: Directory to save the model
            save_tokenizer: Whether to also save the tokenizer
            merge_adapter: Whether to merge adapter weights with base model
            
        Returns:
            Path to the saved model
        """
        if self.model is None:
            raise ValueError("Model has not been initialized or trained")
            
        os.makedirs(save_dir, exist_ok=True)
        
        if merge_adapter and hasattr(self.model, "merge_and_unload"):
            logger.info("Merging adapter weights with base model...")
            merged_model = self.model.merge_and_unload()
            merged_model.save_pretrained(save_dir)
        else:
            self.model.save_pretrained(save_dir)
            
        if save_tokenizer and self.tokenizer is not None:
            self.tokenizer.save_pretrained(save_dir)
            
        logger.info(f"Model saved to {save_dir}")
        return save_dir
    
    def load_adapter(self, adapter_path: str) -> None:
        """
        Load a previously trained adapter.
        
        Args:
            adapter_path: Path to the adapter weights
        """
        if self.model is None:
            self.prepare_model()
            
        self.model.load_adapter(adapter_path)
        logger.info(f"Loaded adapter from {adapter_path}")


def apply_lora(
    model_name_or_path: str,
    dataset: Union[Dataset, DatasetDict],
    output_dir: str = "./lora_output",
    r: int = 8,
    alpha: int = 16,
    dropout: float = 0.05,
    target_modules: Optional[List[str]] = None,
    text_column: str = "formatted_text",
    learning_rate: float = 5e-5,
    num_train_epochs: int = 3,
    per_device_batch_size: int = 4
) -> Tuple[Any, Dict[str, float]]:
    """
    Convenience function to apply LoRA fine-tuning to a model.
    
    Args:
        model_name_or_path: Name or path of the base model
        dataset: Training dataset
        output_dir: Directory to save the model checkpoints
        r: Rank of the update matrices
        alpha: Alpha parameter for LoRA scaling
        dropout: Dropout probability for LoRA layers
        target_modules: Which modules to apply LoRA to
        text_column: Column containing the text to use for training
        learning_rate: Learning rate for training
        num_train_epochs: Number of training epochs
        per_device_batch_size: Batch size per device
        
    Returns:
        Tuple of (trained model, evaluation metrics)
    """
    config = PeftConfig(
        peft_method="lora",
        lora_r=r,
        lora_alpha=alpha,
        lora_dropout=dropout,
        lora_target_modules=target_modules,
        learning_rate=learning_rate,
        num_train_epochs=num_train_epochs,
        per_device_train_batch_size=per_device_batch_size,
        output_dir=output_dir,
    )
    
    fine_tuner = ParameterEfficientFineTuner(model_name_or_path, config)
    return fine_tuner.train(dataset, text_column=text_column, output_dir=output_dir)


def apply_qlora(
    model_name_or_path: str,
    dataset: Union[Dataset, DatasetDict],
    output_dir: str = "./qlora_output",
    r: int = 8,
    alpha: int = 16,
    dropout: float = 0.05,
    target_modules: Optional[List[str]] = None,
    bits: int = 4,
    quant_type: str = "nf4",
    text_column: str = "formatted_text",
    learning_rate: float = 5e-5,
    num_train_epochs: int = 3,
    per_device_batch_size: int = 4
) -> Tuple[Any, Dict[str, float]]:
    """
    Convenience function to apply QLoRA fine-tuning to a model.
    
    Args:
        model_name_or_path: Name or path of the base model
        dataset: Training dataset
        output_dir: Directory to save the model checkpoints
        r: Rank of the update matrices
        alpha: Alpha parameter for LoRA scaling
        dropout: Dropout probability for LoRA layers
        target_modules: Which modules to apply LoRA to
        bits: Bits for quantization (4 or 8)
        quant_type: Quantization type ("nf4", "fp4")
        text_column: Column containing the text to use for training
        learning_rate: Learning rate for training
        num_train_epochs: Number of training epochs
        per_device_batch_size: Batch size per device
        
    Returns:
        Tuple of (trained model, evaluation metrics)
    """
    config = PeftConfig(
        peft_method="qlora",
        lora_r=r,
        lora_alpha=alpha,
        lora_dropout=dropout,
        lora_target_modules=target_modules,
        quantization_bits=bits,
        quantization_type=quant_type,
        learning_rate=learning_rate,
        num_train_epochs=num_train_epochs,
        per_device_train_batch_size=per_device_batch_size,
        output_dir=output_dir,
        fp16=True,  # QLoRA typically uses mixed precision
    )
    
    fine_tuner = ParameterEfficientFineTuner(model_name_or_path, config)
    return fine_tuner.train(dataset, text_column=text_column, output_dir=output_dir)


def merge_adapter_weights(model_with_adapter, save_path: Optional[str] = None) -> Any:
    """
    Merge adapter weights with the base model weights.
    
    This function merges the trained adapter weights into the base model,
    resulting in a model with the adapter's knowledge baked in.
    
    Args:
        model_with_adapter: A model with adapter weights attached
        save_path: Optional path to save the merged model
        
    Returns:
        The merged model
    """
    if not hasattr(model_with_adapter, "merge_and_unload"):
        raise ValueError("The provided model does not support adapter merging")
        
    logger.info("Merging adapter weights with base model...")
    merged_model = model_with_adapter.merge_and_unload()
    
    if save_path:
        os.makedirs(save_path, exist_ok=True)
        merged_model.save_pretrained(save_path)
        logger.info(f"Merged model saved to {save_path}")
        
    return merged_model