"""
Trainer functionality for LLM fine-tuning.

This module provides:
- A customizable trainer for fine-tuning language models
- Training configuration and argument management
- Callbacks for monitoring training progress
- Utilities for saving and loading models during training
"""

import os
import time
import math
import json
import logging
from typing import Dict, List, Any, Union, Optional, Callable, Tuple, Iterator
from dataclasses import dataclass, field
from pathlib import Path

import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
from torch.optim import Optimizer, AdamW
from torch.optim.lr_scheduler import LambdaLR
from transformers import (
    PreTrainedModel,
    PreTrainedTokenizer,
    get_scheduler,
    get_linear_schedule_with_warmup,
    TrainingArguments as HFTrainingArguments,
    Trainer as HFTrainer,
)

from ..evaluation.evaluator import Evaluator

logger = logging.getLogger(__name__)


@dataclass
class TrainingArguments:
    """Arguments for fine-tuning a model"""
    
    # Basic training parameters
    output_dir: str = "output"
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 8
    per_device_eval_batch_size: int = 8
    gradient_accumulation_steps: int = 1
    learning_rate: float = 5e-5
    weight_decay: float = 0.01
    
    # Optimization parameters
    max_grad_norm: float = 1.0
    optimizer_type: str = "adamw"
    lr_scheduler_type: str = "linear"
    warmup_steps: int = 0
    warmup_ratio: float = 0.0
    
    # Logging and evaluation
    logging_steps: int = 100
    eval_steps: int = 500
    save_steps: int = 1000
    save_total_limit: Optional[int] = 3
    
    # Hardware
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    fp16: bool = False
    bf16: bool = False
    
    # Other parameters
    seed: int = 42
    push_to_hub: bool = False
    hub_model_id: Optional[str] = None
    hub_token: Optional[str] = None
    
    def to_hf_training_args(self) -> HFTrainingArguments:
        """Convert to HuggingFace TrainingArguments"""
        return HFTrainingArguments(
            output_dir=self.output_dir,
            num_train_epochs=self.num_train_epochs,
            per_device_train_batch_size=self.per_device_train_batch_size,
            per_device_eval_batch_size=self.per_device_eval_batch_size,
            gradient_accumulation_steps=self.gradient_accumulation_steps,
            learning_rate=self.learning_rate,
            weight_decay=self.weight_decay,
            max_grad_norm=self.max_grad_norm,
            adam_beta1=0.9,
            adam_beta2=0.999,
            adam_epsilon=1e-8,
            lr_scheduler_type=self.lr_scheduler_type,
            warmup_steps=self.warmup_steps,
            warmup_ratio=self.warmup_ratio,
            logging_steps=self.logging_steps,
            eval_steps=self.eval_steps,
            save_steps=self.save_steps,
            save_total_limit=self.save_total_limit,
            fp16=self.fp16,
            bf16=self.bf16,
            seed=self.seed,
            push_to_hub=self.push_to_hub,
            hub_model_id=self.hub_model_id,
            hub_token=self.hub_token,
        )


@dataclass
class TrainingConfig:
    """Configuration for fine-tuning a model"""
    
    model_name_or_path: str
    args: TrainingArguments = field(default_factory=TrainingArguments)
    use_peft: bool = False
    peft_config: Optional[Dict[str, Any]] = None
    quantization: Optional[str] = None  # "4bit", "8bit", or None
    use_hf_trainer: bool = True
    evaluation_metrics: List[str] = field(default_factory=lambda: ["loss"])
    gradient_checkpointing: bool = False
    max_length: int = 2048
    use_flash_attention: bool = False
    preprocessing_config: Optional[Dict[str, Any]] = None


@dataclass
class TrainingCallback:
    """Callback for tracking training progress"""
    
    on_init: Optional[Callable[[Any], None]] = None
    on_epoch_begin: Optional[Callable[[int, Any], None]] = None
    on_epoch_end: Optional[Callable[[int, Dict[str, float], Any], None]] = None
    on_step_begin: Optional[Callable[[int, Any], None]] = None
    on_step_end: Optional[Callable[[int, Dict[str, float], Any], None]] = None
    on_evaluate: Optional[Callable[[Dict[str, float], Any], None]] = None
    on_save: Optional[Callable[[str, Any], None]] = None
    on_train_begin: Optional[Callable[[Any], None]] = None
    on_train_end: Optional[Callable[[Dict[str, float], Any], None]] = None


@dataclass
class TrainingResult:
    """Results of a training run"""
    
    model_path: str
    training_time: float
    metrics: Dict[str, float]
    history: List[Dict[str, float]]
    best_model_path: Optional[str] = None
    checkpoint_paths: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class FineTuningTrainer:
    """
    Trainer for fine-tuning language models.
    
    This class provides methods for fine-tuning language models, handling
    both custom training loops and HuggingFace's Trainer integration.
    """
    
    def __init__(
        self,
        model: PreTrainedModel,
        tokenizer: Optional[PreTrainedTokenizer] = None,
        config: Optional[TrainingConfig] = None,
        train_dataset: Optional[Dataset] = None,
        eval_dataset: Optional[Dataset] = None,
        callbacks: Optional[List[TrainingCallback]] = None,
    ):
        """
        Initialize a fine-tuning trainer.
        
        Args:
            model: Pre-trained model to fine-tune
            tokenizer: Tokenizer for the model (optional if using HF Trainer)
            config: Training configuration
            train_dataset: Dataset for training
            eval_dataset: Dataset for evaluation
            callbacks: Callbacks for monitoring training progress
        """
        self.model = model
        self.tokenizer = tokenizer
        self.config = config or TrainingConfig(model_name_or_path="")
        self.train_dataset = train_dataset
        self.eval_dataset = eval_dataset
        self.callbacks = callbacks or []
        
        # Initialize variables
        self.optimizer = None
        self.scheduler = None
        self.hf_trainer = None
        self.best_eval_metric = float('inf')
        self.history = []
        self.start_time = None
        self.device = torch.device(self.config.args.device)
        
        # Set up the model
        self._setup_model()
        
        # Notify callbacks
        self._call_callbacks("on_init", self)
    
    def _setup_model(self):
        """Set up the model for training"""
        # Move model to device
        self.model.to(self.device)
        
        # Enable gradient checkpointing if requested
        if self.config.gradient_checkpointing and hasattr(self.model, "gradient_checkpointing_enable"):
            self.model.gradient_checkpointing_enable()
        
        # Set up PEFT (Parameter-Efficient Fine-Tuning) if requested
        if self.config.use_peft:
            self._setup_peft()
        
        # Set up HuggingFace trainer if requested
        if self.config.use_hf_trainer:
            self._setup_hf_trainer()
    
    def _setup_peft(self):
        """Set up parameter-efficient fine-tuning"""
        if not self.config.peft_config:
            logger.warning("use_peft is True, but no peft_config provided. Skipping PEFT setup.")
            return
            
        try:
            from peft import get_peft_model, prepare_model_for_kbit_training, LoraConfig, TaskType
            
            # Prepare model for quantization if needed
            if self.config.quantization:
                self.model = prepare_model_for_kbit_training(self.model)
            
            # Create PEFT config
            peft_config_type = self.config.peft_config.get("type", "lora")
            
            if peft_config_type == "lora":
                peft_config = LoraConfig(
                    r=self.config.peft_config.get("r", 8),
                    lora_alpha=self.config.peft_config.get("lora_alpha", 16),
                    lora_dropout=self.config.peft_config.get("lora_dropout", 0.05),
                    bias=self.config.peft_config.get("bias", "none"),
                    task_type=TaskType.CAUSAL_LM,
                    target_modules=self.config.peft_config.get("target_modules", None),
                )
            else:
                raise ValueError(f"Unsupported PEFT config type: {peft_config_type}")
            
            # Apply PEFT to model
            self.model = get_peft_model(self.model, peft_config)
            self.model.print_trainable_parameters()
            
            logger.info(f"Set up PEFT with config type: {peft_config_type}")
            
        except ImportError:
            logger.error("Failed to import peft. Please install it with: pip install peft")
            raise
    
    def _setup_hf_trainer(self):
        """Set up HuggingFace Trainer"""
        if not self.config.use_hf_trainer:
            return
            
        # Set up training arguments
        training_args = self.config.args.to_hf_training_args()
        
        # Create HF Trainer
        self.hf_trainer = HFTrainer(
            model=self.model,
            args=training_args,
            train_dataset=self.train_dataset,
            eval_dataset=self.eval_dataset,
            tokenizer=self.tokenizer,
        )
        
        logger.info("Set up HuggingFace Trainer")
    
    def _create_optimizer(self) -> Optimizer:
        """Create optimizer for training"""
        no_decay = ["bias", "LayerNorm.weight"]
        optimizer_grouped_parameters = [
            {
                "params": [p for n, p in self.model.named_parameters() 
                          if not any(nd in n for nd in no_decay) and p.requires_grad],
                "weight_decay": self.config.args.weight_decay,
            },
            {
                "params": [p for n, p in self.model.named_parameters() 
                          if any(nd in n for nd in no_decay) and p.requires_grad],
                "weight_decay": 0.0,
            },
        ]
        
        optimizer_type = self.config.args.optimizer_type.lower()
        
        if optimizer_type == "adamw":
            return AdamW(
                optimizer_grouped_parameters,
                lr=self.config.args.learning_rate,
                betas=(0.9, 0.999),
                eps=1e-8,
            )
        else:
            raise ValueError(f"Unsupported optimizer type: {optimizer_type}")
    
    def _create_scheduler(self, optimizer: Optimizer, num_training_steps: int) -> LambdaLR:
        """Create learning rate scheduler"""
        scheduler_type = self.config.args.lr_scheduler_type.lower()
        
        warmup_steps = self.config.args.warmup_steps
        if self.config.args.warmup_ratio > 0:
            warmup_steps = int(num_training_steps * self.config.args.warmup_ratio)
        
        if scheduler_type == "linear":
            return get_linear_schedule_with_warmup(
                optimizer,
                num_warmup_steps=warmup_steps,
                num_training_steps=num_training_steps,
            )
        else:
            return get_scheduler(
                name=scheduler_type,
                optimizer=optimizer,
                num_warmup_steps=warmup_steps,
                num_training_steps=num_training_steps,
            )
    
    def _create_dataloader(self, dataset: Dataset, batch_size: int, shuffle: bool = False) -> DataLoader:
        """Create dataloader for training or evaluation"""
        return DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            pin_memory=True,
            drop_last=False,
        )
    
    def train(self) -> TrainingResult:
        """
        Train the model.
        
        Returns:
            TrainingResult with training metrics and model paths
        """
        self.start_time = time.time()
        
        # Notify callbacks
        self._call_callbacks("on_train_begin", self)
        
        # Train with HF Trainer or custom loop
        if self.config.use_hf_trainer and self.hf_trainer:
            result = self._train_with_hf_trainer()
        else:
            result = self._train_with_custom_loop()
        
        # Notify callbacks
        self._call_callbacks("on_train_end", result, self)
        
        return result
    
    def _train_with_hf_trainer(self) -> TrainingResult:
        """Train using HuggingFace's Trainer"""
        if not self.train_dataset:
            raise ValueError("train_dataset must be provided for training")
        
        # Train the model
        train_result = self.hf_trainer.train()
        
        # Save the model
        self.hf_trainer.save_model(self.config.args.output_dir)
        
        if self.tokenizer:
            self.tokenizer.save_pretrained(self.config.args.output_dir)
        
        # Create result object
        metrics = train_result.metrics
        history = []
        for log in self.hf_trainer.state.log_history:
            if "loss" in log:
                history.append(log)
        
        # Sort checkpoint paths by step
        checkpoint_dirs = [d for d in os.listdir(self.config.args.output_dir) if d.startswith("checkpoint-")]
        checkpoint_paths = [os.path.join(self.config.args.output_dir, d) for d in checkpoint_dirs]
        
        return TrainingResult(
            model_path=self.config.args.output_dir,
            training_time=time.time() - self.start_time,
            metrics=metrics,
            history=history,
            best_model_path=self.config.args.output_dir,
            checkpoint_paths=checkpoint_paths,
        )
    
    def _train_with_custom_loop(self) -> TrainingResult:
        """Train using a custom training loop"""
        if not self.train_dataset:
            raise ValueError("train_dataset must be provided for training")
        
        # Create data loaders
        train_dataloader = self._create_dataloader(
            self.train_dataset,
            self.config.args.per_device_train_batch_size,
            shuffle=True,
        )
        
        eval_dataloader = None
        if self.eval_dataset:
            eval_dataloader = self._create_dataloader(
                self.eval_dataset,
                self.config.args.per_device_eval_batch_size,
            )
        
        # Calculate total training steps
        num_update_steps_per_epoch = math.ceil(len(train_dataloader) / self.config.args.gradient_accumulation_steps)
        max_train_steps = self.config.args.num_train_epochs * num_update_steps_per_epoch
        
        # Create optimizer and scheduler
        self.optimizer = self._create_optimizer()
        self.scheduler = self._create_scheduler(self.optimizer, max_train_steps)
        
        # FP16/BF16 setup
        scaler = None
        if self.config.args.fp16:
            from torch.cuda.amp import autocast, GradScaler
            scaler = GradScaler()
        
        # Training loop
        global_step = 0
        self.model.train()
        
        for epoch in range(int(self.config.args.num_train_epochs)):
            # Notify callbacks
            self._call_callbacks("on_epoch_begin", epoch, self)
            
            epoch_start_time = time.time()
            running_loss = 0.0
            
            for step, batch in enumerate(train_dataloader):
                # Move batch to device
                batch = {k: v.to(self.device) for k, v in batch.items()}
                
                # Notify callbacks
                self._call_callbacks("on_step_begin", global_step, self)
                
                # Forward pass
                if self.config.args.fp16:
                    with autocast():
                        outputs = self.model(**batch)
                        loss = outputs.loss / self.config.args.gradient_accumulation_steps
                else:
                    outputs = self.model(**batch)
                    loss = outputs.loss / self.config.args.gradient_accumulation_steps
                
                # Backward pass
                if self.config.args.fp16:
                    scaler.scale(loss).backward()
                else:
                    loss.backward()
                
                running_loss += loss.item()
                
                # Update weights if gradient accumulation is done
                if (step + 1) % self.config.args.gradient_accumulation_steps == 0:
                    # Clip gradients
                    if self.config.args.max_grad_norm > 0:
                        if self.config.args.fp16:
                            scaler.unscale_(self.optimizer)
                        torch.nn.utils.clip_grad_norm_(
                            self.model.parameters(), self.config.args.max_grad_norm
                        )
                    
                    # Update weights
                    if self.config.args.fp16:
                        scaler.step(self.optimizer)
                        scaler.update()
                    else:
                        self.optimizer.step()
                    
                    # Update learning rate
                    self.scheduler.step()
                    
                    # Zero gradients
                    self.optimizer.zero_grad()
                    
                    # Increment global step
                    global_step += 1
                    
                    # Log metrics
                    if global_step % self.config.args.logging_steps == 0:
                        step_metrics = {
                            "loss": running_loss * self.config.args.gradient_accumulation_steps / self.config.args.logging_steps,
                            "epoch": epoch + step / len(train_dataloader),
                            "learning_rate": self.scheduler.get_last_lr()[0],
                        }
                        
                        self.history.append(step_metrics)
                        running_loss = 0.0
                        
                        # Notify callbacks
                        self._call_callbacks("on_step_end", global_step, step_metrics, self)
                    
                    # Evaluate
                    if eval_dataloader and global_step % self.config.args.eval_steps == 0:
                        eval_metrics = self._evaluate(eval_dataloader)
                        
                        # Notify callbacks
                        self._call_callbacks("on_evaluate", eval_metrics, self)
                        
                        # Save best model
                        eval_metric = eval_metrics.get("eval_loss", float('inf'))
                        if eval_metric < self.best_eval_metric:
                            self.best_eval_metric = eval_metric
                            best_model_path = os.path.join(self.config.args.output_dir, "best_model")
                            self._save_model(best_model_path)
                        
                        # Back to training mode
                        self.model.train()
                    
                    # Save checkpoint
                    if global_step % self.config.args.save_steps == 0:
                        checkpoint_dir = os.path.join(self.config.args.output_dir, f"checkpoint-{global_step}")
                        self._save_model(checkpoint_dir)
                        
                        # Notify callbacks
                        self._call_callbacks("on_save", checkpoint_dir, self)
            
            # End of epoch
            epoch_time = time.time() - epoch_start_time
            epoch_metrics = {
                "epoch": epoch,
                "epoch_time": epoch_time,
                "epoch_loss": running_loss * self.config.args.gradient_accumulation_steps / (
                    step % self.config.args.gradient_accumulation_steps + 1
                ),
            }
            
            # Notify callbacks
            self._call_callbacks("on_epoch_end", epoch, epoch_metrics, self)
        
        # Save final model
        final_model_path = os.path.join(self.config.args.output_dir, "final_model")
        self._save_model(final_model_path)
        
        # Collect checkpoint paths
        checkpoint_dirs = [d for d in os.listdir(self.config.args.output_dir) 
                          if d.startswith("checkpoint-") or d in ["best_model", "final_model"]]
        checkpoint_paths = [os.path.join(self.config.args.output_dir, d) for d in checkpoint_dirs]
        
        # Create result object
        final_metrics = {
            "train_loss": self.history[-1]["loss"] if self.history else 0.0,
            "eval_loss": self.best_eval_metric,
            "total_steps": global_step,
        }
        
        return TrainingResult(
            model_path=final_model_path,
            training_time=time.time() - self.start_time,
            metrics=final_metrics,
            history=self.history,
            best_model_path=os.path.join(self.config.args.output_dir, "best_model"),
            checkpoint_paths=checkpoint_paths,
        )
    
    def _evaluate(self, eval_dataloader: DataLoader) -> Dict[str, float]:
        """
        Evaluate the model on the provided dataloader.
        
        Args:
            eval_dataloader: DataLoader with evaluation data
            
        Returns:
            Dictionary of evaluation metrics
        """
        self.model.eval()
        eval_loss = 0.0
        num_eval_steps = 0
        
        # Evaluation loop
        for batch in eval_dataloader:
            batch = {k: v.to(self.device) for k, v in batch.items()}
            
            with torch.no_grad():
                outputs = self.model(**batch)
            
            eval_loss += outputs.loss.item()
            num_eval_steps += 1
        
        # Calculate metrics
        metrics = {
            "eval_loss": eval_loss / num_eval_steps,
        }
        
        return metrics
    
    def _save_model(self, output_dir: str):
        """
        Save model to the specified directory.
        
        Args:
            output_dir: Directory to save the model to
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save model
        if hasattr(self.model, "save_pretrained"):
            self.model.save_pretrained(output_dir)
        else:
            torch.save(self.model.state_dict(), os.path.join(output_dir, "pytorch_model.bin"))
        
        # Save tokenizer if available
        if self.tokenizer:
            self.tokenizer.save_pretrained(output_dir)
        
        # Save training config
        with open(os.path.join(output_dir, "training_config.json"), "w") as f:
            # Convert dataclass to dict
            config_dict = {
                "model_name_or_path": self.config.model_name_or_path,
                "use_peft": self.config.use_peft,
                "quantization": self.config.quantization,
                "use_hf_trainer": self.config.use_hf_trainer,
                "evaluation_metrics": self.config.evaluation_metrics,
                "gradient_checkpointing": self.config.gradient_checkpointing,
                "max_length": self.config.max_length,
            }
            
            json.dump(config_dict, f, indent=2)
        
        logger.info(f"Saved model checkpoint to {output_dir}")
    
    def _call_callbacks(self, event: str, *args, **kwargs):
        """Call all callbacks for the given event"""
        for callback in self.callbacks:
            callback_func = getattr(callback, event, None)
            if callback_func:
                try:
                    callback_func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in callback {event}: {e}")
    
    @classmethod
    def from_pretrained(
        cls,
        model_name_or_path: str,
        config: Optional[TrainingConfig] = None,
        tokenizer_name_or_path: Optional[str] = None,
        **kwargs
    ) -> "FineTuningTrainer":
        """
        Create a trainer from a pre-trained model.
        
        Args:
            model_name_or_path: Name or path of the pre-trained model
            config: Training configuration
            tokenizer_name_or_path: Name or path of the tokenizer
            **kwargs: Additional arguments for the trainer
            
        Returns:
            Initialized FineTuningTrainer
        """
        from transformers import AutoModelForCausalLM, AutoTokenizer
        
        # Create config if not provided
        if config is None:
            config = TrainingConfig(model_name_or_path=model_name_or_path)
        else:
            # Update model name/path
            config.model_name_or_path = model_name_or_path
        
        # Create output directory
        os.makedirs(config.args.output_dir, exist_ok=True)
        
        # Load model with quantization if specified
        model_kwargs = {}
        
        if config.quantization == "4bit":
            try:
                import bitsandbytes as bnb
                from transformers import BitsAndBytesConfig
                
                model_kwargs["quantization_config"] = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.bfloat16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                )
                logger.info("Using 4-bit quantization")
            except ImportError:
                logger.warning("bitsandbytes not found, skipping 4-bit quantization")
                
        elif config.quantization == "8bit":
            model_kwargs["load_in_8bit"] = True
            logger.info("Using 8-bit quantization")
        
        # Add flash attention if specified
        if config.use_flash_attention:
            try:
                model_kwargs["attn_implementation"] = "flash_attention_2"
                logger.info("Using Flash Attention 2")
            except Exception:
                logger.warning("Failed to enable Flash Attention 2, falling back to standard attention")
        
        # Load model
        model = AutoModelForCausalLM.from_pretrained(
            model_name_or_path,
            device_map="auto" if config.args.device == "cuda" else None,
            torch_dtype=torch.bfloat16 if config.args.bf16 else (torch.float16 if config.args.fp16 else None),
            **model_kwargs
        )
        
        # Load tokenizer
        tokenizer_path = tokenizer_name_or_path or model_name_or_path
        tokenizer = AutoTokenizer.from_pretrained(
            tokenizer_path, 
            padding_side="right",
            use_fast=True,
        )
        
        # Add required special tokens
        if tokenizer.pad_token is None and tokenizer.eos_token is not None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Create trainer
        return cls(
            model=model,
            tokenizer=tokenizer,
            config=config,
            **kwargs
        )