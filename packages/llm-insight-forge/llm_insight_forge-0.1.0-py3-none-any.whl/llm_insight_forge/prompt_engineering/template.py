"""
Prompt template system for creating, managing, and rendering LLM prompts.

This module provides a flexible template system for both text-based and chat-based
prompts, supporting variable substitution, conditional blocks, and few-shot examples.
"""

import re
import json
from typing import Dict, List, Any, Union, Optional, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


class TemplateError(Exception):
    """Exception raised for errors in the template system"""
    pass


class BaseTemplate(ABC):
    """Base class for all prompt templates"""
    
    @abstractmethod
    def render(self, **kwargs) -> str:
        """Render the template with the provided variable values"""
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to a dictionary representation"""
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseTemplate':
        """Create a template from a dictionary representation"""
        pass


class PromptTemplate(BaseTemplate):
    """
    Template for text-based prompts with variable substitution.
    
    Supports:
    - Variable substitution using {variable_name} syntax
    - Optional blocks using {% if condition %}...{% endif %} syntax
    - Iteration using {% for item in items %}...{% endfor %} syntax
    """
    
    def __init__(
        self, 
        template: str,
        template_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a prompt template.
        
        Args:
            template: Template string with variables in {var} format
            template_type: Type of template ('text' or a specific model format)
            metadata: Optional metadata about the template
        """
        self.template = template
        self.template_type = template_type
        self.metadata = metadata or {}
        
        # Extract variable names from the template
        self.variables = self._extract_variables()
    
    def _extract_variables(self) -> List[str]:
        """Extract variable names from the template string"""
        # Match {variable} patterns (single curly braces)
        var_pattern = r'\{(\w+)\}'
        matches = re.findall(var_pattern, self.template)
        return list(set(matches))
    
    def render(self, **kwargs) -> str:
        """
        Render the template with the provided variable values.
        
        Args:
            **kwargs: Variable values to substitute in the template
        
        Returns:
            Rendered prompt string
        
        Raises:
            TemplateError: If a required variable is missing
        """
        result = self.template
        
        # Check for missing variables
        missing_vars = [var for var in self.variables if var not in kwargs]
        if missing_vars:
            raise TemplateError(
                f"Missing required variables: {', '.join(missing_vars)}"
            )
        
        # Process conditional blocks
        if_pattern = r'\{%\s*if\s+(\w+)\s*%\}(.*?)\{%\s*endif\s*%\}'
        if_matches = re.finditer(if_pattern, result, re.DOTALL)
        
        for match in if_matches:
            var_name = match.group(1)
            block_content = match.group(2)
            
            if var_name in kwargs and kwargs[var_name]:
                # Replace the entire if block with its content
                result = result.replace(match.group(0), block_content)
            else:
                # Remove the entire if block
                result = result.replace(match.group(0), "")
        
        # Process for loops
        for_pattern = r'\{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%\}(.*?)\{%\s*endfor\s*%\}'
        for_matches = re.finditer(for_pattern, result, re.DOTALL)
        
        for match in for_matches:
            item_name = match.group(1)
            collection_name = match.group(2)
            block_template = match.group(3)
            
            if collection_name in kwargs and isinstance(kwargs[collection_name], (list, tuple)):
                collection = kwargs[collection_name]
                rendered_items = []
                
                for item in collection:
                    item_content = block_template
                    # Handle variables in the loop
                    if isinstance(item, dict):
                        for k, v in item.items():
                            item_content = item_content.replace(f"{{{item_name}.{k}}}", str(v))
                    else:
                        item_content = item_content.replace(f"{{{item_name}}}", str(item))
                    rendered_items.append(item_content)
                
                # Join all rendered items and replace the for block
                result = result.replace(match.group(0), "".join(rendered_items))
            else:
                # If collection is missing or not iterable, remove the for block
                result = result.replace(match.group(0), "")
        
        # Process variable substitutions using single curly braces
        for var in self.variables:
            if var in kwargs:
                value = kwargs[var]
                if value is None:
                    value = ""
                
                # Replace {var} with the actual value
                result = result.replace(
                    "{" + var + "}",
                    str(value)
                )
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to a dictionary representation"""
        return {
            "type": "prompt_template",
            "template": self.template,
            "template_type": self.template_type,
            "variables": self.variables,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptTemplate':
        """Create a template from a dictionary representation"""
        return cls(
            template=data["template"],
            template_type=data.get("template_type", "text"),
            metadata=data.get("metadata", {})
        )
    
    def __str__(self) -> str:
        """String representation of the template"""
        var_list = ", ".join(self.variables)
        return f"PromptTemplate(variables=[{var_list}])"


@dataclass
class MessageTemplate(BaseTemplate):
    """Base template for chat messages"""
    role: str
    content: str
    
    def render(self, **kwargs) -> Dict[str, str]:
        """Render the message template with the provided variable values"""
        # Create a new PromptTemplate instance to handle variable substitution
        template = PromptTemplate(self.content)
        rendered_content = template.render(**kwargs)
        
        return {
            "role": self.role,
            "content": rendered_content
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message template to a dictionary representation"""
        return {
            "type": "message_template",
            "role": self.role,
            "content": self.content,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MessageTemplate':
        """Create a message template from a dictionary representation"""
        return cls(
            role=data["role"],
            content=data["content"]
        )


class SystemMessageTemplate(MessageTemplate):
    """Template for system messages in chat-based prompts"""
    
    def __init__(self, content: str):
        super().__init__(role="system", content=content)


class UserMessageTemplate(MessageTemplate):
    """Template for user messages in chat-based prompts"""
    
    def __init__(self, content: str):
        super().__init__(role="user", content=content)


class AssistantMessageTemplate(MessageTemplate):
    """Template for assistant messages in chat-based prompts"""
    
    def __init__(self, content: str):
        super().__init__(role="assistant", content=content)


class ChatPromptTemplate(BaseTemplate):
    """
    Template for chat-based prompts with message templates.
    
    Supports:
    - System, user, and assistant message templates
    - Variable substitution in message contents
    """
    
    def __init__(
        self,
        messages: List[MessageTemplate],
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a chat prompt template.
        
        Args:
            messages: List of message templates
            metadata: Optional metadata about the template
        """
        self.messages = messages
        self.metadata = metadata or {}
        
        # Extract all variables from message templates
        self.variables = self._extract_variables()
    
    def _extract_variables(self) -> List[str]:
        """Extract variable names from all message templates"""
        variables = set()
        
        for message in self.messages:
            template = PromptTemplate(message.content)
            variables.update(template.variables)
            
        return list(variables)
    
    def render(self, **kwargs) -> List[Dict[str, str]]:
        """
        Render the chat prompt with the provided variable values.
        
        Args:
            **kwargs: Variable values to substitute in the templates
        
        Returns:
            List of rendered messages in chat format
        """
        rendered_messages = []
        
        for message_template in self.messages:
            rendered_message = message_template.render(**kwargs)
            rendered_messages.append(rendered_message)
            
        return rendered_messages
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert chat prompt template to a dictionary representation"""
        return {
            "type": "chat_prompt_template",
            "messages": [message.to_dict() for message in self.messages],
            "variables": self.variables,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatPromptTemplate':
        """Create a chat prompt template from a dictionary representation"""
        messages = []
        
        for message_data in data["messages"]:
            if message_data["role"] == "system":
                message = SystemMessageTemplate(message_data["content"])
            elif message_data["role"] == "user":
                message = UserMessageTemplate(message_data["content"])
            elif message_data["role"] == "assistant":
                message = AssistantMessageTemplate(message_data["content"])
            else:
                message = MessageTemplate(
                    role=message_data["role"],
                    content=message_data["content"]
                )
                
            messages.append(message)
            
        return cls(
            messages=messages,
            metadata=data.get("metadata", {})
        )
    
    def __str__(self) -> str:
        """String representation of the chat prompt template"""
        var_list = ", ".join(self.variables)
        return f"ChatPromptTemplate(messages={len(self.messages)}, variables=[{var_list}])"


@dataclass
class Example:
    """A few-shot example with input and output"""
    input: Any
    output: str


class FewShotTemplate(PromptTemplate):
    """
    Template for few-shot prompting with examples.
    
    Supports:
    - Variable substitution in both the base template and examples
    - Automatic formatting of examples based on a specified format
    """
    
    def __init__(
        self,
        template: str,
        examples: List[Example],
        example_format: Optional[str] = None,
        example_separator: str = "\n\n",
        template_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a few-shot template.
        
        Args:
            template: Base template string with variables and {examples} placeholder
            examples: List of Example objects with input and output fields
            example_format: Format string for examples (defaults to "Input: {input}\nOutput: {output}")
            example_separator: Separator between examples
            template_type: Type of template ('text' or a specific model format)
            metadata: Optional metadata about the template
        """
        super().__init__(template, template_type, metadata)
        
        self.examples = examples
        self.example_format = example_format or "Input: {input}\nOutput: {output}"
        self.example_separator = example_separator
    
    def render(self, **kwargs) -> str:
        """
        Render the few-shot template with the provided variable values.
        
        Args:
            **kwargs: Variable values to substitute in the template
        
        Returns:
            Rendered prompt string with few-shot examples
        """
        # Format the examples
        formatted_examples = []
        
        for example in self.examples:
            # Handle different types of input
            if isinstance(example.input, dict):
                # Use the dict items as format arguments
                formatted_example = self.example_format.format(
                    input=json.dumps(example.input) if len(example.input) > 1 else next(iter(example.input.values())),
                    output=example.output,
                    **example.input
                )
            else:
                # Use the input as a simple value
                formatted_example = self.example_format.format(
                    input=example.input,
                    output=example.output
                )
            
            formatted_examples.append(formatted_example)
        
        # Join examples with separator
        examples_text = self.example_separator.join(formatted_examples)
        
        # Add examples to kwargs for the base template
        kwargs["examples"] = examples_text
        
        # Render the base template
        return super().render(**kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert few-shot template to a dictionary representation"""
        base_dict = super().to_dict()
        base_dict["type"] = "few_shot_template"
        base_dict["examples"] = [
            {"input": ex.input, "output": ex.output}
            for ex in self.examples
        ]
        base_dict["example_format"] = self.example_format
        base_dict["example_separator"] = self.example_separator
        
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FewShotTemplate':
        """Create a few-shot template from a dictionary representation"""
        examples = [
            Example(input=ex["input"], output=ex["output"])
            for ex in data["examples"]
        ]
        
        return cls(
            template=data["template"],
            examples=examples,
            example_format=data.get("example_format"),
            example_separator=data.get("example_separator", "\n\n"),
            template_type=data.get("template_type", "text"),
            metadata=data.get("metadata", {})
        )