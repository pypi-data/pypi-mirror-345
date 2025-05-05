"""
Fine-tuning module for adapting foundation models to specific domains.

This module provides tools for:
- Preparing and preprocessing datasets for fine-tuning
- Implementing supervised fine-tuning (SFT) for instruction tuning
- Parameter-efficient fine-tuning techniques (LoRA, QLoRA, Adapters)
- Evaluation and hyperparameter optimization during fine-tuning
"""

from .dataset_preparation import (
    prepare_dataset,
    TextToTextDataset,
    ConversationDataset,
    generate_prompt_completion_pairs,
)

from .trainer import (
    FineTuningTrainer,
    TrainingConfig,
    TrainingArguments,
    TrainingCallback,
    TrainingResult,
)

from .sft import (
    train_model,
    supervised_fine_tune,
    SFTConfig,
)

from .parameter_efficient import (
    create_peft_model,
    create_lora_config,
    create_qlora_config,
    create_adapter_config,
    merge_adapter_weights,
)