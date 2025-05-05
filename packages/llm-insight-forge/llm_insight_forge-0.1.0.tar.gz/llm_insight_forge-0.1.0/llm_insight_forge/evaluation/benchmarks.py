"""
Benchmarking tools for evaluating LLMs against standard datasets.

This module provides functionality to:
- Run models against common benchmarks like MMLU, TruthfulQA, HellaSwag, etc.
- Compare performance across different models
- Generate detailed benchmark reports
"""

import json
import time
from typing import Dict, List, Any, Union, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path
import logging

import pandas as pd
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

from .metrics import (
    calculate_bleu,
    calculate_rouge,
    semantic_similarity,
    factuality_score
)

logger = logging.getLogger(__name__)

@dataclass
class BenchmarkConfig:
    """Configuration for a benchmark run"""
    
    name: str
    description: str = ""
    dataset_name: str = ""
    dataset_config: Optional[str] = None
    dataset_split: str = "test"
    metric_functions: List[str] = field(default_factory=lambda: ["factuality_score"])
    input_column: str = "input"
    reference_column: str = "output"
    sample_size: Optional[int] = None
    timeout_per_example: int = 30  # seconds


@dataclass
class BenchmarkResult:
    """Results of a benchmark run"""
    
    config: BenchmarkConfig
    model_name: str
    scores: Dict[str, float]
    example_results: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    run_time_seconds: float = 0.0


STANDARD_BENCHMARKS = {
    "mmlu": BenchmarkConfig(
        name="mmlu",
        description="Massive Multitask Language Understanding",
        dataset_name="cais/mmlu",
        dataset_config="all",
        dataset_split="test",
        input_column="question",
        reference_column="answer",
        metric_functions=["factuality_score", "semantic_similarity"],
    ),
    "truthfulqa": BenchmarkConfig(
        name="truthfulqa",
        description="TruthfulQA: Measuring How Models Mimic Human Falsehoods",
        dataset_name="truthful_qa",
        dataset_config="multiple_choice",
        dataset_split="validation",
        input_column="question",
        reference_column="mc1_targets",
        metric_functions=["factuality_score"],
    ),
    "hellaswag": BenchmarkConfig(
        name="hellaswag",
        description="HellaSwag: Can a Machine Really Finish Your Sentence?",
        dataset_name="hellaswag",
        dataset_split="validation",
        input_column="ctx",
        reference_column="endings",
        metric_functions=["semantic_similarity"],
    ),
}


def get_available_benchmarks() -> Dict[str, BenchmarkConfig]:
    """
    Get the list of available benchmark configurations.
    
    Returns:
        Dictionary of benchmark names to their configurations
    """
    return STANDARD_BENCHMARKS


def run_benchmark(
    model_or_pipeline: Any,
    benchmark_config: Union[str, BenchmarkConfig],
    custom_dataset: Optional[Any] = None,
    generation_kwargs: Optional[Dict[str, Any]] = None,
) -> BenchmarkResult:
    """
    Run a model against a benchmark.
    
    Args:
        model_or_pipeline: HuggingFace model, pipeline, or custom model with a generate method
        benchmark_config: Benchmark name (string) or a BenchmarkConfig object
        custom_dataset: Optional custom dataset instead of loading from HF
        generation_kwargs: Optional kwargs to pass to the model's generate method
        
    Returns:
        BenchmarkResult with scores and per-example results
    """
    start_time = time.time()
    
    # Get the benchmark config if a string is provided
    if isinstance(benchmark_config, str):
        if benchmark_config not in STANDARD_BENCHMARKS:
            raise ValueError(f"Unknown benchmark: {benchmark_config}")
        benchmark_config = STANDARD_BENCHMARKS[benchmark_config]
    
    # Set default generation kwargs
    if generation_kwargs is None:
        generation_kwargs = {"max_new_tokens": 50}
    
    # Load the dataset
    if custom_dataset is not None:
        dataset = custom_dataset
    else:
        try:
            dataset = load_dataset(
                benchmark_config.dataset_name,
                benchmark_config.dataset_config,
                split=benchmark_config.dataset_split,
            )
        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            raise
    
    # Check if we need to limit the sample size
    if benchmark_config.sample_size and benchmark_config.sample_size < len(dataset):
        dataset = dataset.select(range(benchmark_config.sample_size))
    
    # Setup for metric functions
    metric_functions = {}
    for metric_name in benchmark_config.metric_functions:
        if metric_name == "factuality_score":
            from .metrics import factuality_score
            metric_functions[metric_name] = factuality_score
        elif metric_name == "semantic_similarity":
            from .metrics import semantic_similarity
            metric_functions[metric_name] = semantic_similarity
        elif metric_name == "calculate_bleu":
            from .metrics import calculate_bleu
            metric_functions[metric_name] = calculate_bleu
        elif metric_name == "calculate_rouge":
            from .metrics import calculate_rouge
            metric_functions[metric_name] = calculate_rouge
    
    # Extract model name
    if hasattr(model_or_pipeline, "model_name"):
        model_name = model_or_pipeline.model_name
    elif hasattr(model_or_pipeline, "name_or_path"):
        model_name = model_or_pipeline.name_or_path
    elif hasattr(model_or_pipeline, "config") and hasattr(model_or_pipeline.config, "_name_or_path"):
        model_name = model_or_pipeline.config._name_or_path
    else:
        model_name = str(type(model_or_pipeline).__name__)
    
    # Process each example
    example_results = []
    all_scores = {metric: [] for metric in metric_functions}
    
    for i, example in enumerate(dataset):
        try:
            input_text = example[benchmark_config.input_column]
            reference = example[benchmark_config.reference_column]
            
            # Generate response
            if hasattr(model_or_pipeline, "generate"):
                # Assume it's a HuggingFace model
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                inputs = tokenizer(input_text, return_tensors="pt")
                outputs = model_or_pipeline.generate(**inputs, **generation_kwargs)
                response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            elif hasattr(model_or_pipeline, "__call__"):
                # Assume it's a pipeline or callable
                response = model_or_pipeline(input_text, **generation_kwargs)
                if isinstance(response, list) and len(response) > 0:
                    if isinstance(response[0], dict) and "generated_text" in response[0]:
                        response = response[0]["generated_text"]
                    elif isinstance(response[0], str):
                        response = response[0]
            else:
                raise ValueError("Model must have a generate method or be callable")
            
            # Calculate metrics
            example_score = {}
            for metric_name, metric_func in metric_functions.items():
                try:
                    score = metric_func(response, reference)
                    example_score[metric_name] = score
                    all_scores[metric_name].append(score)
                except Exception as e:
                    logger.warning(f"Failed to calculate {metric_name}: {e}")
                    example_score[metric_name] = 0.0
            
            example_results.append({
                "input": input_text,
                "reference": reference,
                "response": response,
                "scores": example_score,
            })
            
        except Exception as e:
            logger.error(f"Error processing example {i}: {e}")
            continue
    
    # Calculate aggregate scores
    aggregate_scores = {}
    for metric, scores in all_scores.items():
        if scores:
            aggregate_scores[metric] = sum(scores) / len(scores)
    
    run_time = time.time() - start_time
    
    return BenchmarkResult(
        config=benchmark_config,
        model_name=model_name,
        scores=aggregate_scores,
        example_results=example_results,
        metadata={
            "num_examples": len(example_results),
            "dataset_info": str(dataset.info) if hasattr(dataset, "info") else "",
        },
        run_time_seconds=run_time,
    )


def benchmark_model(
    model_path_or_name: str,
    benchmarks: Union[List[str], List[BenchmarkConfig]],
    device: str = "cpu",
    **kwargs
) -> Dict[str, BenchmarkResult]:
    """
    Benchmark a model against multiple standard benchmarks.
    
    Args:
        model_path_or_name: HuggingFace model name or path
        benchmarks: List of benchmark names or configurations
        device: Device to run on ('cpu', 'cuda', etc.)
        **kwargs: Additional arguments to pass to run_benchmark
        
    Returns:
        Dictionary mapping benchmark names to their results
    """
    try:
        # Load the model and tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_path_or_name)
        model = AutoModelForCausalLM.from_pretrained(model_path_or_name).to(device)
        
        # Create a text generation pipeline
        pipe = pipeline(
            "text-generation", 
            model=model, 
            tokenizer=tokenizer, 
            device=device,
        )
        
        # Run each benchmark
        results = {}
        for benchmark in benchmarks:
            benchmark_name = benchmark if isinstance(benchmark, str) else benchmark.name
            logger.info(f"Running benchmark: {benchmark_name}")
            results[benchmark_name] = run_benchmark(pipe, benchmark, **kwargs)
        
        return results
    
    except Exception as e:
        logger.error(f"Error benchmarking model: {e}")
        raise


def generate_benchmark_report(
    results: Union[BenchmarkResult, Dict[str, BenchmarkResult]],
    output_path: Optional[str] = None,
    format: str = "json",
) -> Optional[str]:
    """
    Generate a report from benchmark results.
    
    Args:
        results: A single BenchmarkResult or a dictionary of them
        output_path: Optional path to save the report
        format: Report format ('json', 'csv', 'md', 'html')
        
    Returns:
        Path to the generated report if output_path is provided, otherwise None
    """
    if isinstance(results, BenchmarkResult):
        results = {results.config.name: results}
    
    report = {
        "summary": {},
        "details": {}
    }
    
    # Generate summary
    for benchmark_name, result in results.items():
        report["summary"][benchmark_name] = {
            "model": result.model_name,
            "scores": result.scores,
            "run_time_seconds": result.run_time_seconds,
            "num_examples": len(result.example_results),
        }
        
        report["details"][benchmark_name] = {
            "config": {k: str(v) for k, v in result.config.__dict__.items()},
            "example_results": result.example_results[:10],  # Include only first 10 examples
            "metadata": result.metadata,
        }
    
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == "json":
            with open(output_path, "w") as f:
                json.dump(report, f, indent=2)
        elif format == "csv":
            # Convert summary to DataFrame and save as CSV
            summary_data = []
            for benchmark, data in report["summary"].items():
                row = {"benchmark": benchmark, "model": data["model"]}
                for metric, score in data["scores"].items():
                    row[metric] = score
                row["run_time_seconds"] = data["run_time_seconds"]
                row["num_examples"] = data["num_examples"]
                summary_data.append(row)
            
            pd.DataFrame(summary_data).to_csv(output_path, index=False)
        elif format == "md":
            # Generate a markdown report
            with open(output_path, "w") as f:
                f.write("# Benchmark Report\n\n")
                f.write("## Summary\n\n")
                for benchmark, data in report["summary"].items():
                    f.write(f"### {benchmark}\n\n")
                    f.write(f"- Model: {data['model']}\n")
                    f.write("- Scores:\n")
                    for metric, score in data["scores"].items():
                        f.write(f"  - {metric}: {score:.4f}\n")
                    f.write(f"- Run time: {data['run_time_seconds']:.2f} seconds\n")
                    f.write(f"- Number of examples: {data['num_examples']}\n\n")
        elif format == "html":
            # Generate a simple HTML report
            html_content = "<html><body>"
            html_content += "<h1>Benchmark Report</h1>"
            html_content += "<h2>Summary</h2>"
            for benchmark, data in report["summary"].items():
                html_content += f"<h3>{benchmark}</h3>"
                html_content += f"<p>Model: {data['model']}</p>"
                html_content += "<p>Scores:</p><ul>"
                for metric, score in data["scores"].items():
                    html_content += f"<li>{metric}: {score:.4f}</li>"
                html_content += f"</ul><p>Run time: {data['run_time_seconds']:.2f} seconds</p>"
                html_content += f"<p>Number of examples: {data['num_examples']}</p>"
            html_content += "</body></html>"
            
            with open(output_path, "w") as f:
                f.write(html_content)
        
        return str(output_path)
    
    return None