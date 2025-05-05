#!/usr/bin/env python3
"""
Example of using LLM Insight Forge for inference optimization.

This example demonstrates:
1. Model quantization to reduce memory footprint
2. Optimized batch inference with quantized models
3. Benchmarking performance differences
"""

import os
import time
import argparse
from typing import List, Dict, Any

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

import llm_insight_forge as lif
from llm_insight_forge.inference_optimization import (
    quantize_model,
    batch_inference,
    run_inference_benchmark
)


def setup_model(model_name: str) -> tuple:
    """Load the original model for comparison"""
    print(f"Loading original model: {model_name}")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    return model, tokenizer


def compare_inference(
    model_name: str,
    prompts: List[str],
    quantized_model_path: str,
) -> Dict[str, Any]:
    """Compare original vs quantized model inference times"""
    results = {}
    
    # Test original model
    print("\nRunning benchmark on original model...")
    original_model, original_tokenizer = setup_model(model_name)
    
    start = time.time()
    original_outputs = []
    for prompt in prompts:
        inputs = original_tokenizer(prompt, return_tensors="pt").to(original_model.device)
        with torch.no_grad():
            outputs = original_model.generate(**inputs, max_new_tokens=128)
        original_outputs.append(original_tokenizer.decode(outputs[0], skip_special_tokens=True))
    original_time = time.time() - start
    
    # Test quantized model with batch inference
    print("\nRunning benchmark on quantized model with batch inference...")
    start = time.time()
    quantized_outputs = batch_inference(
        model_path=quantized_model_path,
        input_texts=prompts,
        batch_size=4,
        use_4bit=True,
        max_length=128
    )
    quantized_time = time.time() - start
    
    # Compare results
    results["original_time"] = original_time
    results["quantized_time"] = quantized_time
    results["speedup"] = original_time / quantized_time if quantized_time > 0 else 0
    
    print(f"\nResults:")
    print(f"Original model time: {original_time:.2f} seconds")
    print(f"Quantized model time: {quantized_time:.2f} seconds")
    print(f"Speed improvement: {results['speedup']:.2f}x")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Model inference optimization example")
    parser.add_argument("--model", type=str, default="meta-llama/Llama-2-7b-hf",
                      help="Model name or path")
    parser.add_argument("--method", type=str, default="bnb_4bit",
                      choices=["bnb_4bit", "bnb_8bit", "dynamic_int8"],
                      help="Quantization method to use")
    args = parser.parse_args()
    
    print("LLM Insight Forge - Inference Optimization Example")
    print("=" * 50)
    
    # Sample prompts for testing
    prompts = [
        "What are the key differences between transformers and RNNs?",
        "Explain quantum computing in simple terms.",
        "Write a haiku about artificial intelligence.",
        "Summarize the history of deep learning in a paragraph.",
    ]
    
    # Quantize model
    print(f"\nQuantizing model {args.model} with {args.method}...")
    result = quantize_model(
        model_name_or_path=args.model,
        method=args.method,
        bits=4 if args.method == "bnb_4bit" else 8,
    )
    
    print("\nQuantization Results:")
    print(f"Original size: {result['original_size_mb']:.2f} MB")
    print(f"Quantized size: {result['quantized_size_mb']:.2f} MB")
    print(f"Compression ratio: {result['compression_ratio']:.2f}x")
    
    # Compare inference performance
    benchmark_results = compare_inference(
        model_name=args.model,
        prompts=prompts,
        quantized_model_path=result["output_path"]
    )
    
    print("\nInference Optimization Example Completed!")


if __name__ == "__main__":
    main()