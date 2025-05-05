#!/usr/bin/env python3
"""
Example of using LLM Insight Forge for model fine-tuning.

This example demonstrates:
1. Preparing datasets for fine-tuning
2. Applying parameter-efficient fine-tuning methods (LoRA)
3. Training and evaluating a fine-tuned model
"""

import os
import argparse
from typing import Dict, List, Any, Optional
import json
import tempfile

import torch
import pandas as pd
from datasets import Dataset

try:
    from transformers import (
        AutoModelForCausalLM, AutoTokenizer,
        TrainingArguments, Trainer
    )
    from peft import LoraConfig, get_peft_model, TaskType, PeftModel
except ImportError:
    print("This example requires additional dependencies:")
    print("pip install transformers peft datasets pandas")
    import sys
    sys.exit(1)

import llm_insight_forge as lif


def create_sample_dataset():
    """Create a small sample dataset for demonstration"""
    print("\n=== Creating Sample Dataset ===")
    
    # Create a sample instruction dataset
    sample_data = [
        {
            "instruction": "Summarize the following text:",
            "input": "Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to natural intelligence displayed by animals including humans. AI research has been defined as the field of study of intelligent agents, which refers to any system that perceives its environment and takes actions that maximize its chance of achieving its goals.",
            "output": "AI is machine intelligence that perceives its environment and takes actions to achieve goals, in contrast to the natural intelligence of humans and animals."
        },
        {
            "instruction": "Translate the following English text to French:",
            "input": "Hello, how are you today?",
            "output": "Bonjour, comment allez-vous aujourd'hui?"
        },
        {
            "instruction": "Write a haiku about:",
            "input": "artificial intelligence",
            "output": "Silicon thinking\nDreams in electric pulses\nHuman-like, yet not"
        },
        {
            "instruction": "Explain the concept of:",
            "input": "quantum computing",
            "output": "Quantum computing uses quantum bits or qubits which, unlike classical bits, can exist in superposition states. This allows quantum computers to perform certain calculations exponentially faster than classical computers for specific problems like factoring large numbers or searching databases."
        },
        {
            "instruction": "Define the term:",
            "input": "machine learning",
            "output": "Machine learning is a subset of AI that focuses on developing algorithms that allow computers to learn patterns from data and make decisions without explicit programming for each specific task."
        }
    ]
    
    # Create a temporary file to store the dataset
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl') as f:
        for item in sample_data:
            f.write(json.dumps(item) + '\n')
            
    print(f"Created sample dataset with {len(sample_data)} examples")
    return f.name


def prepare_dataset(data_path):
    """Prepare dataset for fine-tuning"""
    print("\n=== Preparing Dataset ===")
    
    # Load data from JSONL file
    data = []
    with open(data_path, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    
    print(f"Loaded {len(data)} examples from {data_path}")
    
    # Format data as instruction tuning pairs
    formatted_data = []
    for item in data:
        instruction = item["instruction"]
        input_text = item.get("input", "")
        output = item.get("output", "")
        
        if input_text:
            prompt = f"{instruction}\n\n{input_text}"
        else:
            prompt = instruction
            
        formatted_data.append({
            "prompt": prompt,
            "response": output
        })
    
    # Convert to Dataset object
    df = pd.DataFrame(formatted_data)
    dataset = Dataset.from_pandas(df)
    
    print(f"Dataset prepared with {len(dataset)} examples")
    print("Sample formatted prompt:")
    print("-" * 40)
    print(formatted_data[0]["prompt"])
    print("-" * 40)
    print(formatted_data[0]["response"])
    
    return dataset


def tokenize_dataset(dataset, tokenizer, max_length=512):
    """Tokenize the dataset"""
    print("\n=== Tokenizing Dataset ===")
    
    def tokenize_function(examples):
        # Format as instruction with EOS token
        prompts = examples["prompt"]
        responses = examples["response"]
        
        # Tokenize inputs
        tokenized_inputs = tokenizer(
            prompts, 
            truncation=True,
            max_length=max_length,
            padding="max_length",
            return_tensors="pt"
        )
        
        # Tokenize responses with special handling
        tokenized_outputs = tokenizer(
            responses,
            truncation=True,
            max_length=max_length,
            padding="max_length",
            return_tensors="pt"
        )
        
        # Create labels (set prompt tokens to -100 to ignore in loss)
        input_ids = tokenized_inputs["input_ids"]
        labels = tokenized_outputs["input_ids"].clone()
        
        return {
            "input_ids": input_ids,
            "attention_mask": tokenized_inputs["attention_mask"],
            "labels": labels
        }
    
    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=dataset.column_names
    )
    
    print(f"Tokenized dataset with {len(tokenized_dataset)} examples")
    return tokenized_dataset


def train_with_lora(model_name, dataset_path, output_dir="./fine_tuned_model"):
    """Fine-tune a model using LoRA"""
    print("\n=== Fine-tuning with LoRA ===")
    
    # Prepare dataset
    raw_dataset_path = dataset_path or create_sample_dataset()
    dataset = prepare_dataset(raw_dataset_path)
    
    # Load base model and tokenizer
    print(f"Loading base model: {model_name}")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if not tokenizer.pad_token:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Tokenize dataset
    tokenized_dataset = tokenize_dataset(dataset, tokenizer)
    
    # Split dataset
    split_dataset = tokenized_dataset.train_test_split(test_size=0.2)
    
    # Configure LoRA
    print("Applying LoRA configuration...")
    lora_config = LoraConfig(
        r=16,  # Rank
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type=TaskType.CAUSAL_LM,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"]
    )
    
    # Apply LoRA to model
    peft_model = get_peft_model(model, lora_config)
    print(f"Trainable parameters: {peft_model.print_trainable_parameters()}")
    
    # Configure training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=3,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        gradient_accumulation_steps=2,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        logging_dir=f"{output_dir}/logs",
        logging_steps=10,
        learning_rate=1e-4,
        weight_decay=0.01,
        fp16=True,
        load_best_model_at_end=True,
        report_to="none",
    )
    
    # Create trainer
    trainer = Trainer(
        model=peft_model,
        args=training_args,
        train_dataset=split_dataset["train"],
        eval_dataset=split_dataset["test"],
    )
    
    # Train model (disable for demonstration purposes)
    print("In a real scenario, we would now train the model with:")
    print("trainer.train()")
    # trainer.train()  # Uncomment to actually train the model
    
    # Save model
    print(f"\nSaving model to {output_dir}")
    # trainer.save_model(output_dir)  # Uncomment to save the model
    
    # Clean up temp file if we created one
    if dataset_path is None and os.path.exists(raw_dataset_path):
        os.unlink(raw_dataset_path)
        print(f"Cleaned up temporary dataset file")
    
    print("\nFine-tuning complete!")
    return output_dir
    

def evaluate_fine_tuned_model(model_path, prompt):
    """Evaluate a fine-tuned model on a sample prompt"""
    print("\n=== Evaluating Fine-tuned Model ===")
    
    try:
        # Load the model
        print(f"Loading fine-tuned model from {model_path}")
        model = PeftModel.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        # Generate text
        print(f"Generating response for prompt: {prompt}")
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            output_tokens = model.generate(
                **inputs,
                max_new_tokens=100,
                temperature=0.7
            )
        
        response = tokenizer.decode(output_tokens[0], skip_special_tokens=True)
        
        print("\nGenerated response:")
        print("-" * 40)
        print(response)
        print("-" * 40)
        
        return response
        
    except Exception as e:
        print(f"Error evaluating model: {e}")
        print("Since we didn't actually train the model in this example, this is expected.")
        return None


def main():
    parser = argparse.ArgumentParser(description="LLM fine-tuning example")
    parser.add_argument("--model", type=str, default="facebook/opt-125m",
                      help="Base model to fine-tune (small model for demo)")
    parser.add_argument("--dataset", type=str, default=None,
                      help="Path to dataset file (JSONL format)")
    parser.add_argument("--output-dir", type=str, default="./fine_tuned_model",
                      help="Directory to save fine-tuned model")
    args = parser.parse_args()
    
    print("LLM Insight Forge - Fine-tuning Example")
    print("=" * 50)
    print("NOTE: This example doesn't actually train the model to save time/resources.")
    print("      It demonstrates the setup process for fine-tuning.")
    
    # Run the fine-tuning process
    model_path = train_with_lora(
        model_name=args.model,
        dataset_path=args.dataset,
        output_dir=args.output_dir
    )
    
    # Evaluate (this will likely fail without actual training)
    test_prompt = "Explain the concept of: deep learning"
    evaluate_fine_tuned_model(model_path, test_prompt)
    
    print("\nFine-tuning Example Completed!")


if __name__ == "__main__":
    main()