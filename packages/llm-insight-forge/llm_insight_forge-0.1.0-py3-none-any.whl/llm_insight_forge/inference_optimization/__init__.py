"""
Inference Optimization Module

This module provides tools and techniques for optimizing inference with large language models:
- Quantization methods for reducing model size and increasing inference speed
- Caching strategies for efficient token generation
- Batching techniques for parallel processing
- Speculative decoding for faster generation
"""

from typing import Dict, List, Any, Union, Optional

# Export quantization components
from .quantization import (
    ModelQuantizer,
    QuantizationMethod,
    QuantizationConfig,
    QuantizationResult,
    quantize_model,
    batch_inference,
    run_inference_benchmark,
)

__all__ = [
    "ModelQuantizer",
    "QuantizationMethod", 
    "QuantizationConfig",
    "QuantizationResult",
    "quantize_model",
    "batch_inference",
    "run_inference_benchmark",
]