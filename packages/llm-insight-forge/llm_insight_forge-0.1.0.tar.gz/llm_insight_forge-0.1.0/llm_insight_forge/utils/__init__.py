"""
Utility functions and shared components for LLM Insight Forge.

This module provides common utilities used across different components:
- Logging and monitoring utilities
- Common data structures and helper classes
- File and data handling utilities
- Model loading and inference helpers
"""

from typing import Dict, List, Any, Union, Optional, Callable
import os
import json
import logging
from pathlib import Path

# Configure logging
logger = logging.getLogger("llm_insight_forge")

def configure_logging(
    level: int = logging.INFO,
    log_to_file: bool = False,
    log_file_path: Optional[str] = None
) -> logging.Logger:
    """
    Configure the logger for LLM Insight Forge.
    
    Args:
        level: Logging level (default: INFO)
        log_to_file: Whether to log to a file
        log_file_path: Path to log file (if logging to file)
        
    Returns:
        The configured logger
    """
    logger.setLevel(level)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    
    # Add console handler to logger
    logger.addHandler(console_handler)
    
    # Add file handler if requested
    if log_to_file:
        file_path = log_file_path or "llm_insight_forge.log"
        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def save_json(data: Any, file_path: Union[str, Path]) -> None:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        file_path: Path to save the file
    """
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(file_path: Union[str, Path]) -> Any:
    """
    Load data from a JSON file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        The loaded data
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        The path as a Path object
    """
    path = Path(path)
    os.makedirs(path, exist_ok=True)
    return path


__all__ = [
    "configure_logging",
    "save_json",
    "load_json",
    "ensure_directory",
    "logger",
]