"""
Prompt Engineering module for creating, managing, and optimizing LLM prompts.

This module provides tools for:
- Creating and managing parameterized prompt templates
- Optimizing prompts for better quality responses
- Detecting and preventing jailbreak attempts
- Analyzing prompt effectiveness
"""

from .template import (
    PromptTemplate, 
    ChatPromptTemplate,
    SystemMessageTemplate,
    UserMessageTemplate,
    AssistantMessageTemplate,
    FewShotTemplate,
)

from .optimizer import (
    optimize_prompt,
    PromptOptimizer,
    OptimizationStrategy,
    PromptOptimizationResult,
)

from .jailbreak_detector import (
    detect_jailbreak,
    JailbreakDetector,
    JailbreakDetectionResult,
)