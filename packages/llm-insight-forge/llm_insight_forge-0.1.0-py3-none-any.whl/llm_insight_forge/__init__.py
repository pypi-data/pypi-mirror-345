"""
LLM Insight Forge - A comprehensive toolkit for LLM evaluation, prompt engineering, fine-tuning, and inference optimization.

Created by Biswanath Roul
"""

__version__ = "0.1.0"
__author__ = "Biswanath Roul"

from . import evaluation
from . import prompt_engineering
from . import fine_tuning
from . import inference_optimization
from . import utils

# Convenience imports for common functionality
from .evaluation import (
    benchmark_model,
    evaluate_response,
)
from .prompt_engineering import (
    PromptTemplate,
    optimize_prompt,
)
from .fine_tuning import (
    prepare_dataset,
    train_model,
)
from .inference_optimization import (
    quantize_model,
    batch_inference,
)