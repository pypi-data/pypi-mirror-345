"""
Core evaluator classes and functions for assessing model outputs.

This module provides a comprehensive framework for evaluating LLM responses
against various quality dimensions using configurable evaluation metrics.
"""

import time
from typing import Dict, List, Any, Union, Optional, Callable, Type
from dataclasses import dataclass, field
import logging

from .metrics import (
    calculate_bleu,
    calculate_rouge,
    semantic_similarity,
    factuality_score,
    hallucination_detection,
    bias_detection,
    coherence_score
)

logger = logging.getLogger(__name__)


@dataclass
class EvaluationMetrics:
    """Collection of evaluation metrics for LLM outputs"""
    
    # Text similarity metrics
    bleu: Optional[float] = None
    rouge: Optional[Dict[str, Dict[str, float]]] = None
    semantic_similarity: Optional[float] = None
    
    # Content quality metrics
    factuality: Optional[float] = None
    hallucination_score: Optional[float] = None
    coherence: Optional[float] = None
    
    # Bias and fairness metrics
    bias_scores: Optional[Dict[str, float]] = None
    
    # Custom metrics
    custom: Optional[Dict[str, float]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to a flat dictionary"""
        result = {}
        
        # Add all non-None attributes
        for key, value in self.__dict__.items():
            if value is not None and key != "custom":
                if isinstance(value, dict) and key == "rouge":
                    # Flatten ROUGE scores
                    for rouge_type, scores in value.items():
                        for score_type, score in scores.items():
                            result[f"{rouge_type}_{score_type}"] = score
                elif isinstance(value, dict) and key == "bias_scores":
                    # Flatten bias scores
                    for bias_type, score in value.items():
                        result[f"bias_{bias_type}"] = score
                else:
                    result[key] = value
        
        # Add custom metrics
        for key, value in self.custom.items():
            result[key] = value
        
        return result


@dataclass
class EvaluationResult:
    """Result of evaluating a single response"""
    
    prompt: str
    response: str
    reference: Optional[str] = None
    metrics: EvaluationMetrics = field(default_factory=EvaluationMetrics)
    metadata: Dict[str, Any] = field(default_factory=dict)
    evaluation_time: float = 0.0
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = EvaluationMetrics()


class Evaluator:
    """
    Evaluator for assessing LLM responses across multiple dimensions.
    
    This class provides methods for evaluating responses against reference
    texts using configurable metrics, and can output detailed evaluation reports.
    """
    
    def __init__(
        self,
        metrics: Optional[List[str]] = None,
        custom_metrics: Optional[Dict[str, Callable]] = None,
    ):
        """
        Initialize an evaluator with specified metrics.
        
        Args:
            metrics: List of metric names to use for evaluation
                (options: "bleu", "rouge", "semantic_similarity", "factuality",
                 "hallucination", "coherence", "bias")
            custom_metrics: Dictionary mapping metric names to callable functions
                that take (response, reference) and return a score
        """
        self.metrics = metrics or ["semantic_similarity", "factuality", "coherence"]
        self.custom_metrics = custom_metrics or {}
        
        # Validation
        valid_metrics = [
            "bleu", "rouge", "semantic_similarity", 
            "factuality", "hallucination", "coherence", "bias"
        ]
        for metric in self.metrics:
            if metric not in valid_metrics and metric not in self.custom_metrics:
                logger.warning(f"Unknown metric: {metric}")
    
    def evaluate_response(
        self, 
        response: str, 
        prompt: str = "",
        reference: Optional[str] = None,
        metric_kwargs: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> EvaluationResult:
        """
        Evaluate a single response.
        
        Args:
            response: Model response to evaluate
            prompt: Original prompt that generated the response
            reference: Reference text for comparison (ground truth)
            metric_kwargs: Optional kwargs for specific metrics
                Format: {"metric_name": {"kwarg1": value1, ...}}
        
        Returns:
            EvaluationResult with calculated metrics
        """
        start_time = time.time()
        metric_kwargs = metric_kwargs or {}
        
        metrics = EvaluationMetrics()
        
        # Only evaluate metrics that require reference if reference is provided
        if reference is not None:
            # Apply standard metrics based on configuration
            if "bleu" in self.metrics:
                metrics.bleu = calculate_bleu(
                    reference, 
                    response, 
                    **metric_kwargs.get("bleu", {})
                )
            
            if "rouge" in self.metrics:
                metrics.rouge = calculate_rouge(
                    reference, 
                    response, 
                    **metric_kwargs.get("rouge", {})
                )
            
            if "semantic_similarity" in self.metrics:
                metrics.semantic_similarity = semantic_similarity(
                    reference, 
                    response
                )
            
            if "factuality" in self.metrics:
                metrics.factuality = factuality_score(
                    response, 
                    reference, 
                    **metric_kwargs.get("factuality", {})
                )
            
            if "hallucination" in self.metrics:
                hallucination_results = hallucination_detection(
                    response, 
                    reference, 
                    **metric_kwargs.get("hallucination", {})
                )
                metrics.hallucination_score = hallucination_results["hallucination_score"]
        
        # Metrics that don't require a reference
        if "coherence" in self.metrics:
            metrics.coherence = coherence_score(response)
        
        if "bias" in self.metrics:
            metrics.bias_scores = bias_detection(
                response, 
                **metric_kwargs.get("bias", {})
            )
        
        # Apply custom metrics
        for metric_name, metric_func in self.custom_metrics.items():
            if metric_name in self.metrics:
                try:
                    if reference is not None:
                        score = metric_func(response, reference)
                    else:
                        # Try to call without reference, fall back to None if it fails
                        try:
                            score = metric_func(response)
                        except TypeError:
                            logger.warning(
                                f"Custom metric {metric_name} requires a reference, "
                                "but none was provided."
                            )
                            score = None
                    
                    if score is not None:
                        metrics.custom[metric_name] = score
                except Exception as e:
                    logger.error(f"Error calculating custom metric {metric_name}: {e}")
        
        evaluation_time = time.time() - start_time
        
        return EvaluationResult(
            prompt=prompt,
            response=response,
            reference=reference,
            metrics=metrics,
            evaluation_time=evaluation_time
        )
    
    def evaluate_batch(
        self, 
        responses: List[str],
        prompts: Optional[List[str]] = None,
        references: Optional[List[str]] = None,
        metric_kwargs: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> List[EvaluationResult]:
        """
        Evaluate a batch of responses.
        
        Args:
            responses: List of model responses to evaluate
            prompts: List of prompts that generated the responses
            references: List of reference texts for comparison
            metric_kwargs: Optional kwargs for specific metrics
        
        Returns:
            List of EvaluationResult objects with calculated metrics
        """
        results = []
        
        # Ensure prompts is at least an empty list of the right length
        if prompts is None:
            prompts = [""] * len(responses)
        elif len(prompts) != len(responses):
            logger.warning(
                f"Length mismatch: {len(prompts)} prompts vs {len(responses)} responses. "
                "Padding with empty strings."
            )
            prompts = prompts + [""] * (len(responses) - len(prompts))
        
        # Handle references similarly
        ref_provided = references is not None
        if not ref_provided:
            references = [None] * len(responses)
        elif len(references) != len(responses):
            logger.warning(
                f"Length mismatch: {len(references)} references vs {len(responses)} "
                "responses. Padding with None."
            )
            references = references + [None] * (len(responses) - len(references))
        
        # Process each example
        for i, (prompt, response, reference) in enumerate(zip(prompts, responses, references)):
            try:
                result = self.evaluate_response(
                    response, 
                    prompt, 
                    reference, 
                    metric_kwargs
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Error evaluating response {i}: {e}")
                # Add a placeholder result
                results.append(EvaluationResult(
                    prompt=prompt,
                    response=response,
                    reference=reference,
                    metadata={"error": str(e)}
                ))
        
        return results
    
    def get_aggregate_metrics(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Calculate aggregate metrics from a list of evaluation results.
        
        Args:
            results: List of EvaluationResult objects
            
        Returns:
            Dictionary with aggregated metrics
        """
        if not results:
            return {}
        
        # Collect all metrics
        all_metrics = {}
        
        for result in results:
            metrics_dict = result.metrics.to_dict()
            for key, value in metrics_dict.items():
                if key not in all_metrics:
                    all_metrics[key] = []
                
                # Ensure we only aggregate numeric values
                if isinstance(value, (int, float)):
                    all_metrics[key].append(value)
        
        # Calculate aggregates
        aggregates = {}
        for key, values in all_metrics.items():
            if values:
                aggregates[key] = {
                    "mean": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values),
                }
        
        return aggregates


def evaluate_response(
    response: str,
    reference: Optional[str] = None,
    metrics: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Convenience function to evaluate a single response.
    
    Args:
        response: Model response to evaluate
        reference: Reference text for comparison
        metrics: List of metrics to use
    
    Returns:
        Dictionary with evaluation metrics
    """
    evaluator = Evaluator(metrics=metrics)
    result = evaluator.evaluate_response(response, reference=reference)
    return result.metrics.to_dict()


def evaluate_batch(
    responses: List[str],
    references: Optional[List[str]] = None,
    metrics: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Convenience function to evaluate a batch of responses.
    
    Args:
        responses: List of model responses to evaluate
        references: List of reference texts
        metrics: List of metrics to use
    
    Returns:
        Dictionary with aggregated evaluation metrics
    """
    evaluator = Evaluator(metrics=metrics)
    results = evaluator.evaluate_batch(responses, references=references)
    return evaluator.get_aggregate_metrics(results)