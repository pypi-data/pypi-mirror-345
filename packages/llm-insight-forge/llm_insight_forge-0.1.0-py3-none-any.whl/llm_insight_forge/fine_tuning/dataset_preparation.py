"""
Dataset preparation tools for fine-tuning LLMs.

This module provides tools for:
- Converting raw data into formats suitable for fine-tuning
- Cleaning and preprocessing text data
- Creating instruction-following datasets
- Generating synthetic data for fine-tuning
"""

import re
import json
import random
from typing import List, Dict, Any, Union, Optional, Tuple, Iterator, Callable
from dataclasses import dataclass, field
import logging
from pathlib import Path
import csv

import pandas as pd
import numpy as np
from tqdm import tqdm
from datasets import Dataset, DatasetDict, load_dataset
import torch
from torch.utils.data import Dataset as TorchDataset

logger = logging.getLogger(__name__)

# Add the missing classes and function

class TextToTextDataset(TorchDataset):
    """
    A PyTorch Dataset for text-to-text tasks like instruction tuning.
    
    This dataset works with tokenized inputs and can be used for encoder-decoder
    and decoder-only models.
    """
    
    def __init__(
        self,
        data: Union[Dataset, List[Dict[str, str]]],
        tokenizer,
        input_field: str = "input",
        output_field: str = "output",
        max_input_length: int = 512,
        max_output_length: int = 512,
        add_eos_token: bool = True,
    ):
        """
        Initialize the dataset.
        
        Args:
            data: HF dataset or list of dictionaries with input and output fields
            tokenizer: Tokenizer for encoding inputs and outputs
            input_field: Field name for inputs in the dataset
            output_field: Field name for outputs in the dataset
            max_input_length: Maximum length for inputs
            max_output_length: Maximum length for outputs
            add_eos_token: Whether to add EOS token to outputs
        """
        self.tokenizer = tokenizer
        self.input_field = input_field
        self.output_field = output_field
        self.max_input_length = max_input_length
        self.max_output_length = max_output_length
        self.add_eos_token = add_eos_token
        
        # Convert to list if it's a HF Dataset
        if isinstance(data, Dataset):
            self.examples = data.to_dict()
            self.size = len(data)
        else:
            self.examples = {
                self.input_field: [ex[self.input_field] for ex in data],
                self.output_field: [ex[self.output_field] for ex in data]
            }
            self.size = len(data)
    
    def __len__(self):
        return self.size
        
    def __getitem__(self, idx):
        input_text = self.examples[self.input_field][idx]
        output_text = self.examples[self.output_field][idx]
        
        # Tokenize inputs
        tokenized_input = self.tokenizer(
            input_text,
            max_length=self.max_input_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        # Tokenize outputs
        tokenized_output = self.tokenizer(
            output_text,
            max_length=self.max_output_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        # Remove batch dimension that the tokenizer adds
        input_ids = tokenized_input["input_ids"].squeeze(0)
        attention_mask = tokenized_input["attention_mask"].squeeze(0)
        labels = tokenized_output["input_ids"].squeeze(0)
        
        # Replace padding tokens in labels with -100 so they're ignored in the loss
        labels = torch.where(labels != self.tokenizer.pad_token_id, labels, torch.tensor(-100))
        
        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels
        }


class ConversationDataset(TorchDataset):
    """
    A PyTorch Dataset for conversation data with multiple turns.
    
    This dataset handles formatting multi-turn conversations for models
    like ChatGPT, Claude, etc.
    """
    
    def __init__(
        self,
        data: Union[Dataset, List[Dict[str, Any]]],
        tokenizer,
        conversation_field: str = "conversation",
        max_length: int = 2048,
        speaker_tokens: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize the dataset.
        
        Args:
            data: HF dataset or list of dictionaries with conversation data
            tokenizer: Tokenizer for encoding conversations
            conversation_field: Field name for conversations in the dataset
            max_length: Maximum length for tokenized conversations
            speaker_tokens: Optional mapping of speaker roles to special tokens
        """
        self.tokenizer = tokenizer
        self.conversation_field = conversation_field
        self.max_length = max_length
        self.speaker_tokens = speaker_tokens or {
            "user": "<|user|>",
            "assistant": "<|assistant|>",
            "system": "<|system|>"
        }
        
        # Convert to list if it's a HF Dataset
        if isinstance(data, Dataset):
            self.conversations = list(data)
        else:
            self.conversations = data
            
    def __len__(self):
        return len(self.conversations)
        
    def __getitem__(self, idx):
        conversation = self.conversations[idx][self.conversation_field]
        
        # Format conversation with speaker tokens
        formatted_text = ""
        for turn in conversation:
            role = turn.get("role", "user").lower()
            content = turn.get("content", "")
            
            speaker_token = self.speaker_tokens.get(role, f"<|{role}|>")
            formatted_text += f"{speaker_token}\n{content}\n"
        
        # Add assistant token at the end to indicate where model should continue
        formatted_text += f"{self.speaker_tokens['assistant']}\n"
        
        # Tokenize
        tokenized = self.tokenizer(
            formatted_text,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        # Find where assistant's last response begins
        input_ids = tokenized["input_ids"].squeeze(0)
        attention_mask = tokenized["attention_mask"].squeeze(0)
        
        # Create labels: -100 for input tokens, actual tokens for output
        # This varies by model; here we assume we're training only on assistant responses
        labels = input_ids.clone()
        
        # Find positions of the last assistant token
        assistant_token_id = self.tokenizer.convert_tokens_to_ids(self.speaker_tokens["assistant"])
        
        # Default: train on full sequence if we can't find assistant token
        assistant_token_positions = (labels == assistant_token_id).nonzero(as_tuple=True)[0]
        if len(assistant_token_positions) > 0:
            last_assistant_pos = assistant_token_positions[-1].item()
            # Set all tokens before the last assistant token to -100
            labels[:last_assistant_pos] = -100
        
        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels
        }


def generate_prompt_completion_pairs(
    template_prompts: List[str],
    example_data: List[Dict[str, str]],
    template_vars: List[str],
    n_samples: int = 100
) -> List[Dict[str, str]]:
    """
    Generate prompt-completion pairs by filling templates with example data.
    
    This function is useful for creating synthetic training data from templates.
    
    Args:
        template_prompts: List of prompt templates with {variable} placeholders
        example_data: List of dictionaries with values for template variables
        template_vars: List of variable names in templates
        n_samples: Number of samples to generate
        
    Returns:
        List of dictionaries with "input" and "output" keys
    """
    results = []
    
    for _ in range(n_samples):
        # Select random template and example
        template = random.choice(template_prompts)
        example = random.choice(example_data)
        
        # Create mapping of template variables to values
        var_map = {}
        for var in template_vars:
            if var in example:
                var_map[var] = example[var]
            else:
                # Skip this example if it's missing a required variable
                break
        else:  # This else belongs to the for loop, executed when no break occurs
            # Fill the template
            try:
                prompt = template.format(**var_map)
                
                # Add to results
                results.append({
                    "input": prompt,
                    "output": example.get("output", "")
                })
            except KeyError as e:
                logger.warning(f"Missing template variable: {e}")
                continue
    
    return results

# ... existing code below ...

@dataclass
class DatasetConfig:
    """Configuration for dataset preparation"""
    
    input_column: str = "input"
    output_column: str = "output"
    text_column: Optional[str] = None  # For single text column datasets
    instruction_column: Optional[str] = None  # Optional explicit instruction column
    format_template: Optional[str] = None  # Template for formatting examples
    train_test_split: float = 0.2  # Fraction for test set
    validation_split: float = 0.1  # Fraction for validation set
    seed: int = 42  # Random seed
    max_length: Optional[int] = None  # Max length of examples


@dataclass
class PreprocessingConfig:
    """Configuration for text preprocessing"""
    
    remove_html: bool = True
    fix_unicode: bool = True
    standardize_whitespace: bool = True
    lowercase: bool = False
    remove_urls: bool = False
    remove_email: bool = False
    normalize_numbers: bool = False
    max_length: Optional[int] = None
    custom_replacements: Dict[str, str] = field(default_factory=dict)


def clean_text(text: str, config: PreprocessingConfig = None) -> str:
    """
    Clean text according to preprocessing config.
    
    Args:
        text: Text to clean
        config: Preprocessing configuration
        
    Returns:
        Cleaned text
    """
    if config is None:
        config = PreprocessingConfig()
        
    if not text:
        return ""
        
    # Fix unicode
    if config.fix_unicode:
        import unicodedata
        text = unicodedata.normalize("NFKC", text)
        
    # Remove HTML
    if config.remove_html:
        text = re.sub(r'<[^>]+>', ' ', text)
        
    # Remove URLs
    if config.remove_urls:
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        
    # Remove email addresses
    if config.remove_email:
        text = re.sub(r'\S+@\S+', '', text)
        
    # Normalize numbers
    if config.normalize_numbers:
        text = re.sub(r'\d+', '0', text)
        
    # Standardize whitespace
    if config.standardize_whitespace:
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
    # Convert to lowercase
    if config.lowercase:
        text = text.lower()
        
    # Apply custom replacements
    for pattern, replacement in config.custom_replacements.items():
        text = re.sub(pattern, replacement, text)
        
    # Truncate if needed
    if config.max_length and len(text) > config.max_length:
        text = text[:config.max_length]
        
    return text


def load_data_from_json(
    file_path: Union[str, Path], 
    config: DatasetConfig = None
) -> Dataset:
    """
    Load data from a JSON file or JSONL file.
    
    Args:
        file_path: Path to JSON/JSONL file
        config: Dataset configuration
        
    Returns:
        Hugging Face dataset
    """
    if config is None:
        config = DatasetConfig()
        
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
        
    try:
        # Try to load as JSONL first
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            try:
                # Check if first line is valid JSON
                json.loads(first_line)
                # If successful, assume JSONL format
                return Dataset.from_json(str(file_path))
            except json.JSONDecodeError:
                # Not JSONL, try loading as regular JSON
                pass
                
        # Try as regular JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Handle different JSON formats
        if isinstance(data, list) and all(isinstance(item, dict) for item in data):
            # List of dictionaries
            return Dataset.from_list(data)
        elif isinstance(data, dict):
            # Check if it's a mapping of split names to examples
            if any(key in data for key in ['train', 'validation', 'test']):
                dataset_dict = {}
                for split_name, split_data in data.items():
                    if isinstance(split_data, list):
                        dataset_dict[split_name] = Dataset.from_list(split_data)
                return DatasetDict(dataset_dict)
            else:
                # Single dictionary with keys as fields
                return Dataset.from_dict(data)
                
        raise ValueError(f"Unsupported JSON format in {file_path}")
        
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        raise


def load_data_from_csv(
    file_path: Union[str, Path],
    config: DatasetConfig = None
) -> Dataset:
    """
    Load data from a CSV file.
    
    Args:
        file_path: Path to CSV file
        config: Dataset configuration
        
    Returns:
        Hugging Face dataset
    """
    if config is None:
        config = DatasetConfig()
        
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
        
    try:
        df = pd.read_csv(file_path)
        return Dataset.from_pandas(df)
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        raise


def load_data_from_text(
    file_path: Union[str, Path],
    config: DatasetConfig = None
) -> Dataset:
    """
    Load data from a text file (one example per line).
    
    Args:
        file_path: Path to text file
        config: Dataset configuration
        
    Returns:
        Hugging Face dataset
    """
    if config is None:
        config = DatasetConfig()
        
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
            
        return Dataset.from_dict({config.text_column or "text": lines})
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        raise


def load_data_from_huggingface(
    dataset_name: str,
    config: DatasetConfig = None,
    split: Optional[str] = None,
    **kwargs
) -> Union[Dataset, DatasetDict]:
    """
    Load a dataset from the Hugging Face Hub.
    
    Args:
        dataset_name: Name of the dataset on HF Hub
        config: Dataset configuration
        split: Optional specific split to load
        **kwargs: Additional arguments for load_dataset
        
    Returns:
        Hugging Face dataset
    """
    try:
        return load_dataset(dataset_name, split=split, **kwargs)
    except Exception as e:
        logger.error(f"Error loading dataset {dataset_name}: {e}")
        raise


def format_instruction_dataset(
    dataset: Union[Dataset, DatasetDict],
    config: DatasetConfig = None,
    preprocessing_config: PreprocessingConfig = None
) -> Union[Dataset, DatasetDict]:
    """
    Format dataset into instruction-following format.
    
    Args:
        dataset: Input dataset
        config: Dataset configuration
        preprocessing_config: Preprocessing configuration
        
    Returns:
        Formatted dataset
    """
    if config is None:
        config = DatasetConfig()
        
    if preprocessing_config is None:
        preprocessing_config = PreprocessingConfig()
    
    # Default template if none provided
    template = config.format_template or "### Instruction:\n{instruction}\n\n### Input:\n{input}\n\n### Response:\n{output}"
    
    def format_example(example):
        """Format a single example"""
        # Clean all text fields
        for key in example:
            if isinstance(example[key], str):
                example[key] = clean_text(example[key], preprocessing_config)
                
        # Determine instruction, input and output
        instruction = ""
        input_text = ""
        output = ""
        
        if config.instruction_column and config.instruction_column in example:
            instruction = example[config.instruction_column]
            
        if config.input_column and config.input_column in example:
            input_text = example[config.input_column]
            
        if config.output_column and config.output_column in example:
            output = example[config.output_column]
            
        # For single text column datasets, use it as input
        if config.text_column and config.text_column in example:
            if not input_text:  # Only use if input is not already set
                input_text = example[config.text_column]
                
        # Format according to template
        formatted_text = template.format(
            instruction=instruction or input_text,
            input=input_text,
            output=output
        )
        
        # Add formatted text to example
        example["formatted_text"] = formatted_text
        
        return example
    
    # Apply formatting to dataset
    if isinstance(dataset, DatasetDict):
        return DatasetDict({
            split: split_dataset.map(format_example)
            for split, split_dataset in dataset.items()
        })
    else:
        return dataset.map(format_example)


def create_train_test_split(
    dataset: Dataset,
    config: DatasetConfig = None
) -> DatasetDict:
    """
    Split dataset into train, validation, and test sets.
    
    Args:
        dataset: Input dataset
        config: Dataset configuration
        
    Returns:
        DatasetDict with train, validation, and test splits
    """
    if config is None:
        config = DatasetConfig()
        
    # Calculate split sizes
    test_size = config.train_test_split
    val_size = config.validation_split
    
    # Make the split
    train_testval = dataset.train_test_split(
        test_size=test_size + val_size,
        seed=config.seed
    )
    
    # Further split test_val into test and validation
    test_val = train_testval["test"]
    if val_size > 0:
        relative_val_size = val_size / (test_size + val_size)
        test_val_split = test_val.train_test_split(
            test_size=relative_val_size,
            seed=config.seed
        )
        return DatasetDict({
            "train": train_testval["train"],
            "validation": test_val_split["test"],
            "test": test_val_split["train"]
        })
    else:
        # No validation set needed
        return DatasetDict({
            "train": train_testval["train"],
            "test": train_testval["test"]
        })


def filter_dataset(
    dataset: Union[Dataset, DatasetDict],
    filter_fn: Callable[[Dict], bool]
) -> Union[Dataset, DatasetDict]:
    """
    Filter dataset based on a filtering function.
    
    Args:
        dataset: Input dataset
        filter_fn: Function that takes an example and returns True to keep it
        
    Returns:
        Filtered dataset
    """
    if isinstance(dataset, DatasetDict):
        return DatasetDict({
            split: split_dataset.filter(filter_fn)
            for split, split_dataset in dataset.items()
        })
    else:
        return dataset.filter(filter_fn)


def save_dataset(
    dataset: Union[Dataset, DatasetDict],
    output_dir: Union[str, Path],
    format: str = "arrow"
) -> None:
    """
    Save dataset to disk.
    
    Args:
        dataset: Dataset to save
        output_dir: Directory to save to
        format: Format to save in ('arrow', 'json', 'csv')
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if isinstance(dataset, DatasetDict):
        for split, split_dataset in dataset.items():
            split_path = output_dir / split
            split_path.mkdir(exist_ok=True)
            
            if format == "arrow":
                split_dataset.save_to_disk(str(split_path))
            elif format == "json":
                split_dataset.to_json(str(split_path / f"{split}.jsonl"))
            elif format == "csv":
                split_dataset.to_csv(str(split_path / f"{split}.csv"))
            else:
                raise ValueError(f"Unsupported format: {format}")
    else:
        if format == "arrow":
            dataset.save_to_disk(str(output_dir))
        elif format == "json":
            dataset.to_json(str(output_dir / "dataset.jsonl"))
        elif format == "csv":
            dataset.to_csv(str(output_dir / "dataset.csv"))
        else:
            raise ValueError(f"Unsupported format: {format}")


def generate_synthetic_dataset(
    base_prompts: List[str],
    output_examples: List[str],
    variations: int = 5,
    output_file: Optional[Union[str, Path]] = None
) -> Dataset:
    """
    Generate synthetic instruction-following data by creating variations.
    
    Args:
        base_prompts: List of base prompt templates
        output_examples: List of example outputs
        variations: Number of variations to create per base prompt
        output_file: Optional path to save the generated dataset
        
    Returns:
        Generated dataset
    """
    data = []
    
    # Create prompt variations
    for prompt in tqdm(base_prompts, desc="Generating variations"):
        for _ in range(variations):
            # Randomly modify prompt with synonyms
            modified_prompt = _create_prompt_variation(prompt)
            
            # Pair with random output
            output = random.choice(output_examples)
            
            data.append({
                "input": modified_prompt,
                "output": output
            })
    
    # Create dataset
    dataset = Dataset.from_list(data)
    
    # Save if requested
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if output_path.suffix == '.json':
            dataset.to_json(str(output_path))
        elif output_path.suffix == '.csv':
            dataset.to_csv(str(output_path))
        else:
            # Default to arrow format
            dataset.save_to_disk(str(output_path))
    
    return dataset


def _create_prompt_variation(prompt: str) -> str:
    """Create a variation of a prompt by substituting words"""
    # Simple word variations (could be expanded)
    variations = {
        "explain": ["describe", "clarify", "elaborate on", "tell me about"],
        "help": ["assist", "aid", "support"],
        "create": ["generate", "make", "produce", "develop"],
        "list": ["enumerate", "itemize", "detail"],
        "what": ["which", "what exactly", "tell me what"],
        "how": ["in what way", "by what means"],
        "why": ["for what reason", "what is the reason"],
    }
    
    result = prompt
    
    # Apply some random variations
    for word, alternatives in variations.items():
        if word in result.lower() and random.random() > 0.5:
            result = re.sub(
                r'\b' + word + r'\b', 
                random.choice(alternatives),
                result,
                flags=re.IGNORECASE,
                count=1
            )
    
    return result


def prepare_dataset(
    data_source: Union[str, Path, Dataset],
    output_dir: Optional[Union[str, Path]] = None,
    config: Optional[DatasetConfig] = None,
    preprocessing_config: Optional[PreprocessingConfig] = None,
    format_for_model: Optional[str] = None,
) -> Union[Dataset, DatasetDict]:
    """
    Convenience function to prepare a dataset for fine-tuning.
    
    Args:
        data_source: Path to data file or dataset object
        output_dir: Directory to save processed dataset
        config: Dataset configuration
        preprocessing_config: Preprocessing configuration
        format_for_model: Optional model-specific format ('llama', 'mistral', etc.)
        
    Returns:
        Processed dataset
    """
    if config is None:
        config = DatasetConfig()
        
    if preprocessing_config is None:
        preprocessing_config = PreprocessingConfig()
    
    # Load data if provided as path
    if isinstance(data_source, (str, Path)):
        path = Path(data_source)
        
        if path.suffix == '.json' or path.suffix == '.jsonl':
            dataset = load_data_from_json(path, config)
        elif path.suffix == '.csv':
            dataset = load_data_from_csv(path, config)
        elif path.suffix == '.txt':
            dataset = load_data_from_text(path, config)
        elif '/' in str(path) and not path.exists():
            # Might be a Hugging Face dataset name
            dataset = load_data_from_huggingface(str(path))
        else:
            raise ValueError(f"Unsupported data format: {path}")
    else:
        dataset = data_source
        
    # Apply model-specific formatting templates
    if format_for_model:
        if format_for_model.lower() in ["llama", "llama2"]:
            config.format_template = "<s>[INST] {instruction} [/INST] {output} </s>"
        elif format_for_model.lower() in ["mistral", "mixtral"]:
            config.format_template = "<s>[INST] {instruction} [/INST] {output} </s>"
        elif format_for_model.lower() == "phi":
            config.format_template = "Instruct: {instruction}\nOutput: {output}"
        elif format_for_model.lower() == "gemma":
            config.format_template = "<start_of_turn>user\n{instruction}<end_of_turn>\n<start_of_turn>model\n{output}<end_of_turn>"
    
    # Format as instruction dataset
    processed_dataset = format_instruction_dataset(
        dataset, 
        config=config,
        preprocessing_config=preprocessing_config
    )
    
    # Create train/test split if it's a single dataset
    if isinstance(processed_dataset, Dataset):
        processed_dataset = create_train_test_split(processed_dataset, config)
    
    # Save if output_dir provided
    if output_dir:
        save_dataset(processed_dataset, output_dir)
    
    return processed_dataset