"""
Supervised Fine-Tuning (SFT) utilities for language models.

This module provides functionality for full fine-tuning of language models
using supervised learning on instruction datasets.
"""

import os
import time
import json
from typing import Dict, List, Any, Union, Optional, Tuple
from dataclasses import dataclass, field
import logging
from pathlib import Path
import warnings

import torch
from torch.utils.data import DataLoader
from transformers import (
    TrainingArguments,
    Trainer,
    AutoModelForCausalLM,
    AutoTokenizer,
    AutoConfig,
    DataCollatorForSeq2Seq,
    PreTrainedTokenizer,
    EarlyStoppingCallback
)
from datasets import Dataset, DatasetDict
from tqdm import tqdm

logger = logging.getLogger(__name__)

# Add the missing functions

def train_model(
    model_name_or_path: str,
    dataset: Union[Dataset, DatasetDict],
    output_dir: str,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Tuple[Any, str]:
    """
    Train a model using supervised fine-tuning.
    
    This is a simplified interface for the SupervisedFineTuner class.
    
    Args:
        model_name_or_path: Name or path of the model to fine-tune
        dataset: Dataset for training
        output_dir: Directory to save the trained model
        config: Optional configuration overrides
        **kwargs: Additional keyword arguments passed to SupervisedFineTuner.train
        
    Returns:
        Tuple of (trained model, output directory path)
    """
    # Convert config dict to SFTConfig
    sft_config = SFTConfig(
        model_name=model_name_or_path,
        output_dir=output_dir,
        **(config or {})
    )
    
    # Initialize fine-tuner
    fine_tuner = SupervisedFineTuner(config=sft_config)
    
    # Train the model
    model, _ = fine_tuner.train(
        dataset=dataset,
        output_dir=output_dir,
        **kwargs
    )
    
    return model, output_dir


def supervised_fine_tune(
    model_name: str,
    train_data: Union[Dataset, List[Dict[str, str]]],
    eval_data: Optional[Union[Dataset, List[Dict[str, str]]]] = None,
    output_dir: str = "./sft_output",
    epochs: int = 3,
    learning_rate: float = 2e-5,
    batch_size: int = 4,
    max_length: int = 1024,
    fp16: bool = False,
    bf16: bool = False,
    input_column: str = "input",
    output_column: str = "output",
    use_peft: bool = False,
    peft_config: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Supervised fine-tuning with simplified interface.
    
    This function provides a simpler interface for fine-tuning, with
    sensible defaults for most parameters.
    
    Args:
        model_name: Name or path of the model to fine-tune
        train_data: Training data as HF Dataset or list of examples
        eval_data: Optional evaluation data
        output_dir: Directory to save the trained model
        epochs: Number of training epochs
        learning_rate: Learning rate for training
        batch_size: Batch size per device
        max_length: Maximum sequence length
        fp16: Whether to use FP16 precision
        bf16: Whether to use BF16 precision
        input_column: Name of input column in dataset
        output_column: Name of output column in dataset
        use_peft: Whether to use parameter-efficient fine-tuning
        peft_config: Configuration for PEFT if used
        
    Returns:
        Path to the saved model
    """
    # Convert list data to Dataset if needed
    if isinstance(train_data, list):
        train_data = Dataset.from_list(train_data)
    if eval_data is not None and isinstance(eval_data, list):
        eval_data = Dataset.from_list(eval_data)
    
    # Combine into DatasetDict if eval data provided
    if eval_data is not None:
        dataset = DatasetDict({
            "train": train_data,
            "validation": eval_data
        })
    else:
        dataset = train_data
    
    # Create config
    config = SFTConfig(
        model_name=model_name,
        num_train_epochs=epochs,
        learning_rate=learning_rate,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        fp16=fp16,
        bf16=bf16,
        output_dir=output_dir,
        model_max_length=max_length,
    )
    
    # If using PEFT, apply it
    if use_peft:
        try:
            from llm_insight_forge.fine_tuning.parameter_efficient import (
                create_peft_model,
                create_lora_config,
            )
            
            # Load base model and tokenizer
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
                
            model = AutoModelForCausalLM.from_pretrained(
                model_name, 
                torch_dtype=torch.float16 if fp16 else (
                    torch.bfloat16 if bf16 else torch.float32
                ),
                device_map="auto"
            )
            
            # Create PEFT model
            peft_config = peft_config or {"r": 8, "lora_alpha": 16}
            lora_config = create_lora_config(**peft_config)
            model = create_peft_model(model, lora_config)
            
            # Train with PEFT model
            fine_tuner = SupervisedFineTuner(config=config, model=model, tokenizer=tokenizer)
            
        except ImportError:
            logger.warning("PEFT requested but packages not available. "
                          "Falling back to full fine-tuning.")
            fine_tuner = SupervisedFineTuner(config=config)
    else:
        # Standard fine-tuning
        fine_tuner = SupervisedFineTuner(config=config)
    
    # Train the model
    _, _ = fine_tuner.train(
        dataset=dataset,
        prompt_column=input_column,
        response_column=output_column,
        output_dir=output_dir,
        max_length=max_length,
    )
    
    # Path where model was saved
    model_path = os.path.join(output_dir, "final_model")
    return model_path


@dataclass
class SFTConfig:
    """Configuration for supervised fine-tuning"""
    
    # Model settings
    model_name: str = "gpt2"  # Base model to fine-tune
    use_gradient_checkpointing: bool = False  # Enable gradient checkpointing
    model_max_length: Optional[int] = None  # Override model max context length
    
    # Training settings
    learning_rate: float = 2e-5
    weight_decay: float = 0.01
    num_train_epochs: float = 3.0
    lr_scheduler_type: str = "cosine"
    warmup_ratio: float = 0.1
    max_steps: int = -1  # Override epochs (-1 means use epochs instead)
    
    # Batch sizes
    per_device_train_batch_size: int = 4
    per_device_eval_batch_size: int = 4
    gradient_accumulation_steps: int = 8
    
    # Optimizer settings
    adam_beta1: float = 0.9
    adam_beta2: float = 0.999
    adam_epsilon: float = 1e-8
    max_grad_norm: float = 1.0
    
    # Precision
    fp16: bool = False
    bf16: bool = False
    
    # Output settings
    output_dir: str = "./sft_output"
    save_strategy: str = "steps"
    save_steps: int = 500
    save_total_limit: int = 3
    
    # Evaluation settings
    evaluation_strategy: str = "steps"
    eval_steps: int = 500
    logging_steps: int = 50
    report_to: List[str] = field(default_factory=lambda: ["tensorboard"])
    
    # Early stopping
    early_stopping_patience: Optional[int] = None
    load_best_model_at_end: bool = True
    metric_for_best_model: str = "loss"
    greater_is_better: bool = False
    
    # Resource utilization
    dataloader_num_workers: int = 0
    
    # Validation settings
    num_validation_samples: Optional[int] = None  # Limit validation samples


class SupervisedFineTuner:
    """
    Fine-tuner for supervised instruction-following.
    
    This class provides methods for full fine-tuning of language models
    on instruction datasets, without parameter-efficient techniques.
    """
    
    def __init__(
        self,
        config: Optional[SFTConfig] = None,
        model=None,
        tokenizer=None,
    ):
        """
        Initialize the supervised fine-tuner.
        
        Args:
            config: Configuration for supervised fine-tuning
            model: Optional pre-loaded model
            tokenizer: Optional pre-loaded tokenizer
        """
        self.config = config or SFTConfig()
        self.model = model
        self.tokenizer = tokenizer
    
    def prepare_model(self) -> None:
        """
        Prepare the model and tokenizer for fine-tuning.
        
        This method loads the base model and configures it for training.
        """
        try:
            # Load tokenizer if not provided
            if self.tokenizer is None:
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.config.model_name,
                    use_fast=True
                )
                
                # Ensure the tokenizer has a pad token
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Override max length if specified
            if self.config.model_max_length:
                self.tokenizer.model_max_length = self.config.model_max_length
            
            # Load model config
            model_config = AutoConfig.from_pretrained(self.config.model_name)
            
            # Enable gradient checkpointing if requested
            if self.config.use_gradient_checkpointing:
                model_config.use_cache = False
                
            # Load model if not provided
            if self.model is None:
                logger.info(f"Loading model: {self.config.model_name}")
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.config.model_name,
                    config=model_config,
                    device_map="auto",
                    torch_dtype=torch.bfloat16 if self.config.bf16 else (
                        torch.float16 if self.config.fp16 else None
                    )
                )
                
            # Enable gradient checkpointing if requested
            if self.config.use_gradient_checkpointing:
                self.model.gradient_checkpointing_enable()
                
            # Log model information
            total_params = sum(p.numel() for p in self.model.parameters())
            logger.info(f"Model loaded with {total_params / 1e6:.2f}M parameters")
            
        except Exception as e:
            logger.error(f"Error preparing model: {e}")
            raise
    
    def _prepare_dataset(
        self,
        dataset: Union[Dataset, DatasetDict],
        prompt_column: str = "input",
        response_column: str = "output",
        text_column: Optional[str] = None,
        format_column: Optional[str] = "formatted_text",
        max_length: Optional[int] = None,
    ) -> Dict[str, Dataset]:
        """
        Prepare datasets for fine-tuning.
        
        Args:
            dataset: Input dataset
            prompt_column: Column containing prompts/instructions
            response_column: Column containing responses/outputs
            text_column: Column containing single text field (alternative to prompt+response)
            format_column: Optional column with pre-formatted text
            max_length: Maximum sequence length for tokenization
            
        Returns:
            Dictionary of tokenized datasets for training and evaluation
        """
        # Extract splits
        train_dataset = None
        eval_dataset = None
        
        if isinstance(dataset, DatasetDict):
            # Use existing splits
            if "train" in dataset:
                train_dataset = dataset["train"]
            if "validation" in dataset:
                eval_dataset = dataset["validation"]
            elif "test" in dataset:
                eval_dataset = dataset["test"]
        else:
            # Use single dataset as training data
            train_dataset = dataset
        
        if train_dataset is None:
            raise ValueError("No training data found in the dataset")

        # Limit validation samples if specified
        if eval_dataset is not None and self.config.num_validation_samples:
            if len(eval_dataset) > self.config.num_validation_samples:
                eval_dataset = eval_dataset.select(
                    range(self.config.num_validation_samples)
                )
        
        # Function to format examples if needed
        def format_example(example):
            if format_column and format_column in example:
                # Use pre-formatted text if available
                return {"text": example[format_column]}
                
            if text_column and text_column in example:
                # Use single text field
                return {"text": example[text_column]}
                
            # Combine prompt and response
            prompt = example.get(prompt_column, "")
            response = example.get(response_column, "")
            
            if not prompt and not response:
                raise ValueError(
                    f"Example missing required fields. "
                    f"Expected '{prompt_column}' and '{response_column}', or '{text_column}'"
                )
                
            # Simple format combining prompt and response
            formatted = prompt + "\n" + response if prompt else response
            return {"text": formatted}
            
        # Apply formatting
        if train_dataset is not None:
            train_dataset = train_dataset.map(format_example)
            
        if eval_dataset is not None:
            eval_dataset = eval_dataset.map(format_example)
            
        # Function to tokenize examples
        def tokenize_function(examples):
            texts = examples["text"]
            
            if not isinstance(texts, list):
                texts = [texts]
                
            # Get the maximum length
            _max_length = max_length or self.tokenizer.model_max_length
                
            # Tokenize inputs
            tokenized = self.tokenizer(
                texts,
                truncation=True,
                padding="max_length",
                max_length=_max_length,
                return_tensors="pt",
            )
            
            # Set labels equal to input_ids for causal LM
            tokenized["labels"] = tokenized["input_ids"].clone()
            
            return tokenized
        
        # Apply tokenization
        if train_dataset is not None:
            tokenized_train = train_dataset.map(
                tokenize_function,
                batched=True,
                remove_columns=[col for col in train_dataset.column_names 
                                if col != "text"],
                desc="Tokenizing train data",
            )
        else:
            tokenized_train = None
            
        if eval_dataset is not None:
            tokenized_eval = eval_dataset.map(
                tokenize_function,
                batched=True,
                remove_columns=[col for col in eval_dataset.column_names 
                                if col != "text"],
                desc="Tokenizing eval data",
            )
        else:
            tokenized_eval = None
            
        result = {}
        if tokenized_train is not None:
            result["train"] = tokenized_train
            
        if tokenized_eval is not None:
            result["eval"] = tokenized_eval
            
        return result
    
    def train(
        self,
        dataset: Union[Dataset, DatasetDict],
        prompt_column: str = "input",
        response_column: str = "output",
        text_column: Optional[str] = None,
        format_column: Optional[str] = "formatted_text",
        output_dir: Optional[str] = None,
        max_length: Optional[int] = None,
        resume_from_checkpoint: Optional[str] = None,
    ) -> Tuple[Any, Dict[str, float]]:
        """
        Train the model with supervised fine-tuning.
        
        Args:
            dataset: Training dataset
            prompt_column: Column containing prompts
            response_column: Column containing responses
            text_column: Column containing single text field
            format_column: Optional column with pre-formatted text
            output_dir: Directory to save checkpoints
            max_length: Maximum sequence length
            resume_from_checkpoint: Path to resume from
            
        Returns:
            Tuple of (trained model, evaluation metrics)
        """
        # Prepare model if not already prepared
        if self.model is None or self.tokenizer is None:
            self.prepare_model()
        
        # Prepare dataset
        tokenized_datasets = self._prepare_dataset(
            dataset=dataset,
            prompt_column=prompt_column,
            response_column=response_column,
            text_column=text_column,
            format_column=format_column,
            max_length=max_length,
        )
        
        # Set up training arguments
        output_dir = output_dir or self.config.output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        training_args = TrainingArguments(
            output_dir=output_dir,
            learning_rate=self.config.learning_rate,
            weight_decay=self.config.weight_decay,
            num_train_epochs=self.config.num_train_epochs,
            lr_scheduler_type=self.config.lr_scheduler_type,
            warmup_ratio=self.config.warmup_ratio,
            max_steps=self.config.max_steps,
            per_device_train_batch_size=self.config.per_device_train_batch_size,
            per_device_eval_batch_size=self.config.per_device_eval_batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            adam_beta1=self.config.adam_beta1,
            adam_beta2=self.config.adam_beta2,
            adam_epsilon=self.config.adam_epsilon,
            max_grad_norm=self.config.max_grad_norm,
            fp16=self.config.fp16,
            bf16=self.config.bf16,
            save_strategy=self.config.save_strategy,
            save_steps=self.config.save_steps,
            save_total_limit=self.config.save_total_limit,
            evaluation_strategy="steps" if "eval" in tokenized_datasets else "no",
            eval_steps=self.config.eval_steps if "eval" in tokenized_datasets else None,
            logging_steps=self.config.logging_steps,
            report_to=self.config.report_to,
            load_best_model_at_end="eval" in tokenized_datasets and self.config.load_best_model_at_end,
            metric_for_best_model=self.config.metric_for_best_model,
            greater_is_better=self.config.greater_is_better,
            dataloader_num_workers=self.config.dataloader_num_workers,
        )
        
        # Set up data collator
        data_collator = DataCollatorForSeq2Seq(
            tokenizer=self.tokenizer, 
            model=self.model,
            pad_to_multiple_of=8 if self.config.fp16 or self.config.bf16 else None,
        )
        
        # Set up callbacks
        callbacks = []
        if self.config.early_stopping_patience:
            callbacks.append(EarlyStoppingCallback(
                early_stopping_patience=self.config.early_stopping_patience
            ))
        
        # Initialize Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_datasets.get("train"),
            eval_dataset=tokenized_datasets.get("eval"),
            data_collator=data_collator,
            tokenizer=self.tokenizer,
            callbacks=callbacks,
        )
        
        # Train the model
        logger.info("Starting training...")
        train_result = trainer.train(resume_from_checkpoint=resume_from_checkpoint)
        
        # Save the final model
        logger.info("Saving model...")
        trainer.save_model(os.path.join(output_dir, "final_model"))
        
        # Save training metrics
        metrics = train_result.metrics
        trainer.log_metrics("train", metrics)
        trainer.save_metrics("train", metrics)
        
        # Evaluate the model
        if "eval" in tokenized_datasets:
            logger.info("Evaluating model...")
            eval_result = trainer.evaluate()
            trainer.log_metrics("eval", eval_result)
            trainer.save_metrics("eval", eval_result)
        else:
            eval_result = {}
        
        return self.model, eval_result
    
    def save_model(self, save_dir: str, save_tokenizer: bool = True) -> str:
        """
        Save the fine-tuned model.
        
        Args:
            save_dir: Directory to save the model
            save_tokenizer: Whether to save the tokenizer
            
        Returns:
            Path to the saved model
        """
        if self.model is None:
            raise ValueError("Model has not been initialized or trained")
            
        os.makedirs(save_dir, exist_ok=True)
        
        self.model.save_pretrained(save_dir)
        
        if save_tokenizer and self.tokenizer is not None:
            self.tokenizer.save_pretrained(save_dir)
            
        logger.info(f"Model saved to {save_dir}")
        return save_dir


def fine_tune_model(
    model_name: str,
    dataset: Union[Dataset, DatasetDict],
    output_dir: str,
    epochs: int = 3,
    learning_rate: float = 2e-5,
    batch_size: int = 4,
    gradient_accumulation_steps: int = 8,
    use_fp16: bool = False,
    use_bf16: bool = False,
    prompt_column: str = "input",
    response_column: str = "output",
    format_column: str = "formatted_text",
) -> Any:
    """
    Convenience function for supervised fine-tuning of a model.
    
    Args:
        model_name: Name or path of base model
        dataset: Training dataset
        output_dir: Directory to save outputs
        epochs: Number of training epochs
        learning_rate: Learning rate
        batch_size: Batch size per device
        gradient_accumulation_steps: Gradient accumulation steps
        use_fp16: Enable FP16 precision
        use_bf16: Enable BF16 precision
        prompt_column: Column containing prompts
        response_column: Column containing responses
        format_column: Column with formatted text (if available)
        
    Returns:
        Trained model
    """
    config = SFTConfig(
        model_name=model_name,
        num_train_epochs=epochs,
        learning_rate=learning_rate,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        fp16=use_fp16,
        bf16=use_bf16,
        output_dir=output_dir,
    )
    
    fine_tuner = SupervisedFineTuner(config)
    model, _ = fine_tuner.train(
        dataset=dataset,
        prompt_column=prompt_column,
        response_column=response_column,
        format_column=format_column,
        output_dir=output_dir,
    )
    
    return model