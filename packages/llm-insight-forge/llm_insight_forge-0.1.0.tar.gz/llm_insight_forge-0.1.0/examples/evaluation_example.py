#!/usr/bin/env python3
"""
Example of using LLM Insight Forge for model evaluation.

This example demonstrates:
1. Using various evaluation metrics to assess model outputs
2. Benchmarking model performance across different inputs
3. Detecting hallucinations and factuality issues
"""

import argparse
import json
from typing import Dict, Any, List
from pprint import pprint

import llm_insight_forge as lif
from llm_insight_forge.evaluation.metrics import (
    calculate_bleu,
    calculate_rouge,
    semantic_similarity,
    factuality_score,
    hallucination_detection,
    bias_detection,
    coherence_score,
)


def evaluate_single_response():
    """Demonstrate evaluation of a single response"""
    print("\n=== Single Response Evaluation ===")
    
    reference = "The Eiffel Tower is a wrought-iron lattice tower located on the Champ de Mars in Paris, France. It was constructed from 1887 to 1889 as the entrance to the 1889 World's Fair."
    response = "The Eiffel Tower is a famous landmark in Paris, France. It was built in 1889 for the World's Fair and stands at 324 meters tall."
    
    # Calculate various metrics
    print("Reference text:")
    print(reference)
    print("\nModel response:")
    print(response)
    print("\nCalculating metrics...")
    
    bleu = calculate_bleu(reference, response)
    rouge = calculate_rouge(reference, response)
    similarity = semantic_similarity(reference, response)
    factuality = factuality_score(response, reference)
    hallucination = hallucination_detection(response, reference)
    bias = bias_detection(response)
    coherence = coherence_score(response)
    
    print(f"\nBLEU score: {bleu:.4f}")
    print(f"ROUGE-L F1 score: {rouge['rougeL']['fmeasure']:.4f}")
    print(f"Semantic similarity: {similarity:.4f}")
    print(f"Factuality score: {factuality:.4f}")
    print(f"Coherence score: {coherence:.4f}")
    
    print("\nHallucination analysis:")
    print(f"  Hallucination detected: {hallucination['hallucination_detected']}")
    print(f"  Hallucination score: {hallucination['hallucination_score']:.4f}")
    
    print("\nBias analysis:")
    for bias_type, score in bias.items():
        print(f"  {bias_type} bias: {score:.4f}")


def demonstrate_batch_evaluation():
    """Demonstrate evaluation of multiple responses"""
    print("\n=== Batch Response Evaluation ===")
    
    # Sample evaluation dataset
    eval_data = [
        {
            "question": "What is the capital of France?",
            "reference": "The capital of France is Paris.",
            "response": "The capital of France is Paris, which is known as the City of Light."
        },
        {
            "question": "How many planets are in our solar system?",
            "reference": "There are eight planets in our solar system: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune.",
            "response": "There are nine planets in our solar system: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune, and Pluto."
        },
        {
            "question": "Who wrote Romeo and Juliet?",
            "reference": "Romeo and Juliet was written by William Shakespeare.",
            "response": "Romeo and Juliet is a famous play written by William Shakespeare in the late 16th century."
        }
    ]
    
    print(f"Evaluating {len(eval_data)} responses...")
    
    # Metrics to calculate
    metrics = ["bleu", "rouge", "semantic_similarity", "factuality", "coherence"]
    results = []
    
    for idx, item in enumerate(eval_data):
        print(f"\nItem {idx+1}: {item['question']}")
        print(f"Reference: {item['reference']}")
        print(f"Response: {item['response']}")
        
        # Calculate metrics
        item_results = {
            "question": item["question"],
            "bleu": calculate_bleu(item["reference"], item["response"]),
            "rouge": calculate_rouge(item["reference"], item["response"])["rougeL"]["fmeasure"],
            "semantic_similarity": semantic_similarity(item["reference"], item["response"]),
            "factuality": factuality_score(item["response"], item["reference"]),
            "coherence": coherence_score(item["response"]),
            "hallucination": hallucination_detection(
                item["response"], item["reference"]
            )["hallucination_detected"],
        }
        
        results.append(item_results)
        
        print("Results:")
        for metric, value in item_results.items():
            if metric != "question":
                print(f"  {metric}: {value:.4f}" if isinstance(value, float) else f"  {metric}: {value}")
    
    # Calculate average scores
    avg_scores = {}
    for metric in ["bleu", "rouge", "semantic_similarity", "factuality", "coherence"]:
        avg_scores[metric] = sum(r[metric] for r in results) / len(results)
    
    print("\nAverage scores across all responses:")
    for metric, value in avg_scores.items():
        print(f"  {metric}: {value:.4f}")
        
    # Count hallucinations
    hallucination_count = sum(1 for r in results if r["hallucination"])
    print(f"Hallucinations detected: {hallucination_count}/{len(results)}")


def demonstrate_factuality_assessment():
    """Demonstrate in-depth factuality assessment"""
    print("\n=== Factuality Assessment ===")
    
    # Reference facts
    reference_facts = [
        "The Earth orbits the Sun.",
        "The Moon orbits the Earth.",
        "The Earth's atmosphere is primarily composed of nitrogen and oxygen.",
        "The Earth has one natural satellite, the Moon.",
    ]
    
    responses = [
        "The Earth orbits the Sun, which is a star at the center of our solar system. The Moon is Earth's only natural satellite. Earth's atmosphere contains mostly nitrogen and oxygen.",
        "The Earth revolves around the Sun and is orbited by the Moon. Earth's atmospheric composition is primarily nitrogen (78%) and oxygen (21%), with trace gases making up the remainder.",
        "The Earth circles the Sun every 365.25 days. The Moon circles Earth every 27.3 days. Earth is surrounded by an atmosphere of nitrogen, oxygen, and carbon dioxide.",
        "The Sun orbits the Earth, completing one revolution every year. The Earth's atmosphere is mostly oxygen. The Moon is one of several natural satellites of Earth.",
    ]
    
    print("Reference facts:")
    for fact in reference_facts:
        print(f"- {fact}")
    
    print("\nEvaluating factuality of responses:")
    for idx, response in enumerate(responses):
        print(f"\nResponse {idx+1}:")
        print(response)
        
        # Calculate factuality using different methods
        fact_score = factuality_score(response, reference_facts, method="fact_matching")
        
        # Detect hallucinations
        hallucination_result = hallucination_detection(response, reference_facts)
        
        print(f"Factuality score: {fact_score:.4f}")
        print(f"Hallucination detected: {hallucination_result['hallucination_detected']}")
        
        if hallucination_result["hallucinations"]:
            print("Potential hallucinations:")
            for sent, score in hallucination_result["hallucinations"]:
                print(f"- '{sent}' (confidence: {score:.2f})")


def main():
    parser = argparse.ArgumentParser(description="LLM evaluation example")
    parser.add_argument("--demo", type=str, default="all",
                      choices=["single", "batch", "factuality", "all"],
                      help="Which demo to run")
    args = parser.parse_args()
    
    print("LLM Insight Forge - Evaluation Example")
    print("=" * 50)
    
    if args.demo in ["single", "all"]:
        evaluate_single_response()
        
    if args.demo in ["batch", "all"]:
        demonstrate_batch_evaluation()
        
    if args.demo in ["factuality", "all"]:
        demonstrate_factuality_assessment()
    
    print("\nEvaluation Example Completed!")


if __name__ == "__main__":
    main()