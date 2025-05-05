"""
Evaluation module for assessing LLM performance across various dimensions.

This module provides tools for:
- Benchmarking models against standard test sets
- Evaluating responses for factuality, relevance, and coherence 
- Detecting hallucinations and biases
- Comparing performance across different models
"""

from .metrics import (
    calculate_bleu,
    calculate_rouge,
    semantic_similarity,
    factuality_score,
    hallucination_detection,
    bias_detection,
    coherence_score,
)

from .benchmarks import (
    run_benchmark,
    benchmark_model,
    generate_benchmark_report,
)

from .evaluator import (
    evaluate_response,
    evaluate_batch,
    EvaluationResult,
    EvaluationMetrics,
)