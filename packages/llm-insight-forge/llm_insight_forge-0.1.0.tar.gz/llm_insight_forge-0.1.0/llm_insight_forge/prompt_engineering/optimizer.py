"""
Prompt optimization tools for improving prompt effectiveness.

This module provides algorithms and strategies to optimize prompts for:
- Better response quality
- Reduced token usage
- Less hallucination
- Improved factuality
"""

import time
import copy
import random
from enum import Enum
from typing import Dict, List, Any, Union, Optional, Callable, Tuple
from dataclasses import dataclass, field
import logging

from ..evaluation import evaluate_response, EvaluationMetrics
from .template import PromptTemplate, ChatPromptTemplate, BaseTemplate

logger = logging.getLogger(__name__)


class OptimizationStrategy(Enum):
    """Strategies for optimizing prompts"""
    
    ITERATIVE = "iterative"  # Iterative refinement based on evaluations
    ABLATION = "ablation"    # Removing prompt components to find minimal effective prompt
    EXPANSION = "expansion"  # Expanding prompt with clarifications and constraints
    A_B_TEST = "a_b_test"    # A/B testing different prompt variations


@dataclass
class PromptVariation:
    """A variation of a prompt with associated metadata and performance metrics"""
    
    prompt: Union[str, List[Dict[str, str]], BaseTemplate]
    description: str
    metrics: Optional[Dict[str, Any]] = None
    score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PromptOptimizationResult:
    """Result of a prompt optimization process"""
    
    original_prompt: Union[str, List[Dict[str, str]], BaseTemplate]
    optimized_prompt: Union[str, List[Dict[str, str]], BaseTemplate]
    improvement: float
    history: List[PromptVariation]
    metrics: Dict[str, Any]
    strategy: OptimizationStrategy
    runtime_seconds: float


class PromptOptimizer:
    """
    Optimizer for improving prompt effectiveness based on specified metrics.
    
    This class implements various strategies to optimize prompts, such as
    iterative refinement, ablation studies, and A/B testing.
    """
    
    def __init__(
        self,
        model: Any,
        metric_functions: Optional[List[str]] = None,
        custom_metric_fn: Optional[Callable] = None,
        optimize_for: str = "factuality",
        strategy: OptimizationStrategy = OptimizationStrategy.ITERATIVE,
        max_iterations: int = 10,
        improvement_threshold: float = 0.01,
    ):
        """
        Initialize a prompt optimizer.
        
        Args:
            model: LLM or inference function to use for testing prompts
            metric_functions: List of metric functions to evaluate prompts
            custom_metric_fn: Optional custom evaluation function
            optimize_for: Metric to optimize for
            strategy: Optimization strategy to use
            max_iterations: Maximum number of optimization iterations
            improvement_threshold: Minimum improvement to continue optimization
        """
        self.model = model
        self.metric_functions = metric_functions or ["factuality", "coherence", "semantic_similarity"]
        self.custom_metric_fn = custom_metric_fn
        self.optimize_for = optimize_for
        self.strategy = strategy
        self.max_iterations = max_iterations
        self.improvement_threshold = improvement_threshold
    
    def _generate_response(self, prompt: Union[str, List[Dict[str, str]]]) -> str:
        """
        Generate a response from the model using the provided prompt.
        
        Args:
            prompt: Text prompt or chat messages
            
        Returns:
            Model's generated response
        """
        try:
            if isinstance(self.model, Callable):
                # Handle callable model functions
                return self.model(prompt)
            
            # Handle different prompt formats
            if isinstance(prompt, str):
                if hasattr(self.model, "generate_text"):
                    return self.model.generate_text(prompt)
                elif hasattr(self.model, "generate"):
                    return self.model.generate(prompt)
                elif hasattr(self.model, "__call__"):
                    result = self.model(prompt)
                    if isinstance(result, str):
                        return result
                    elif isinstance(result, dict) and "generated_text" in result:
                        return result["generated_text"]
                    elif isinstance(result, list) and len(result) > 0:
                        if isinstance(result[0], str):
                            return result[0]
                        elif isinstance(result[0], dict) and "generated_text" in result[0]:
                            return result[0]["generated_text"]
            elif isinstance(prompt, list):
                # Handle chat format
                if hasattr(self.model, "chat"):
                    return self.model.chat(prompt)
                elif hasattr(self.model, "generate"):
                    return self.model.generate(prompt)
                elif hasattr(self.model, "__call__"):
                    result = self.model(prompt)
                    if isinstance(result, str):
                        return result
                    elif isinstance(result, dict) and "generated_text" in result:
                        return result["generated_text"]
            
            # Default fallback - attempt to call the model directly
            return str(self.model(prompt))
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return ""
    
    def _evaluate_prompt(
        self, 
        prompt: Union[str, List[Dict[str, str]]],
        reference: Optional[str] = None,
    ) -> Tuple[Dict[str, Any], float]:
        """
        Evaluate a prompt by generating a response and measuring metrics.
        
        Args:
            prompt: Prompt to evaluate
            reference: Optional reference text for comparison
            
        Returns:
            Tuple of (metrics dict, overall score)
        """
        # Generate response from model
        response = self._generate_response(prompt)
        
        # Calculate metrics
        metrics = evaluate_response(
            response, 
            reference=reference,
            metrics=self.metric_functions
        )
        
        # Calculate custom metric if provided
        if self.custom_metric_fn:
            try:
                custom_score = self.custom_metric_fn(prompt, response, reference)
                metrics["custom"] = custom_score
            except Exception as e:
                logger.error(f"Error calculating custom metric: {e}")
        
        # Calculate overall score based on optimization target
        if self.optimize_for in metrics:
            score = metrics[self.optimize_for]
        elif "factuality" in metrics:
            score = metrics["factuality"]  # Default to factuality
        else:
            # Use first available numeric metric if target not found
            for k, v in metrics.items():
                if isinstance(v, (int, float)):
                    score = v
                    break
            else:
                score = 0.0
        
        return metrics, score
    
    def _optimize_iterative(
        self,
        prompt: Union[str, List[Dict[str, str]], BaseTemplate],
        template_vars: Optional[Dict[str, Any]] = None,
        reference: Optional[str] = None,
    ) -> PromptOptimizationResult:
        """
        Optimize prompt through iterative refinement.
        
        Args:
            prompt: Initial prompt to optimize
            template_vars: Variables for template rendering
            reference: Optional reference for evaluation
            
        Returns:
            Optimization result with best prompt
        """
        start_time = time.time()
        history = []
        
        # Prepare initial prompt
        if isinstance(prompt, BaseTemplate):
            rendered_prompt = prompt.render(**(template_vars or {}))
        else:
            rendered_prompt = prompt
        
        # Evaluate initial prompt
        initial_metrics, initial_score = self._evaluate_prompt(rendered_prompt, reference)
        
        # Add initial version to history
        history.append(PromptVariation(
            prompt=copy.deepcopy(prompt),
            description="Original prompt",
            metrics=initial_metrics,
            score=initial_score
        ))
        
        current_prompt = copy.deepcopy(prompt)
        current_score = initial_score
        best_prompt = copy.deepcopy(prompt)
        best_score = initial_score
        
        # Define improvement strategies
        improvement_strategies = [
            self._add_specificity,
            self._add_constraints,
            self._add_examples,
            self._add_context,
            self._simplify_language,
            self._structure_output,
            self._add_reasoning_steps,
        ]
        
        # Iterative improvement
        for iteration in range(self.max_iterations):
            logger.info(f"Starting optimization iteration {iteration+1}/{self.max_iterations}")
            
            # Try different improvement strategies
            variations = []
            
            for strategy_fn in improvement_strategies:
                try:
                    variation = strategy_fn(current_prompt)
                    
                    # Render if template
                    if isinstance(variation, BaseTemplate):
                        rendered_variation = variation.render(**(template_vars or {}))
                    else:
                        rendered_variation = variation
                    
                    # Evaluate variation
                    metrics, score = self._evaluate_prompt(rendered_variation, reference)
                    
                    variations.append(PromptVariation(
                        prompt=copy.deepcopy(variation),
                        description=f"Iteration {iteration+1}: {strategy_fn.__name__}",
                        metrics=metrics,
                        score=score
                    ))
                    
                except Exception as e:
                    logger.error(f"Error applying strategy {strategy_fn.__name__}: {e}")
            
            # Find best variation
            if variations:
                best_variation = max(variations, key=lambda x: x.score)
                history.extend(variations)
                
                # Check if better than current best
                if best_variation.score > best_score + self.improvement_threshold:
                    best_prompt = copy.deepcopy(best_variation.prompt)
                    best_score = best_variation.score
                    current_prompt = copy.deepcopy(best_variation.prompt)
                    current_score = best_variation.score
                    logger.info(f"Found improvement: {best_score - initial_score:.4f}")
                else:
                    logger.info("No significant improvement found, stopping optimization")
                    break
            else:
                logger.warning("No valid variations produced, stopping optimization")
                break
        
        runtime = time.time() - start_time
        
        # Final evaluation of best prompt
        if isinstance(best_prompt, BaseTemplate):
            rendered_best = best_prompt.render(**(template_vars or {}))
        else:
            rendered_best = best_prompt
            
        final_metrics, _ = self._evaluate_prompt(rendered_best, reference)
        
        return PromptOptimizationResult(
            original_prompt=prompt,
            optimized_prompt=best_prompt,
            improvement=best_score - initial_score,
            history=history,
            metrics=final_metrics,
            strategy=self.strategy,
            runtime_seconds=runtime
        )
    
    def _optimize_ablation(
        self,
        prompt: Union[str, List[Dict[str, str]], BaseTemplate],
        template_vars: Optional[Dict[str, Any]] = None,
        reference: Optional[str] = None,
    ) -> PromptOptimizationResult:
        """
        Optimize prompt through ablation studies (removing components).
        
        Args:
            prompt: Initial prompt to optimize
            template_vars: Variables for template rendering
            reference: Optional reference for evaluation
            
        Returns:
            Optimization result with minimal effective prompt
        """
        start_time = time.time()
        history = []
        
        # Prepare initial prompt
        if isinstance(prompt, BaseTemplate):
            rendered_prompt = prompt.render(**(template_vars or {}))
        else:
            rendered_prompt = prompt
        
        # Evaluate initial prompt
        initial_metrics, initial_score = self._evaluate_prompt(rendered_prompt, reference)
        
        # Add initial version to history
        history.append(PromptVariation(
            prompt=copy.deepcopy(prompt),
            description="Original prompt",
            metrics=initial_metrics,
            score=initial_score
        ))
        
        # For text prompts, split into paragraphs/sections
        sections = []
        if isinstance(prompt, str):
            # Split by double newlines as paragraph boundaries
            raw_sections = prompt.split('\n\n')
            sections = [s for s in raw_sections if s.strip()]
            
            # If few sections, try splitting by single newlines
            if len(sections) <= 2:
                raw_sections = prompt.split('\n')
                sections = [s for s in raw_sections if s.strip()]
        
            # If still few sections, try splitting by sentences
            if len(sections) <= 2:
                import re
                raw_sections = re.split(r'(?<=[.!?])\s+', prompt)
                sections = [s for s in raw_sections if s.strip()]
                
        # For chat prompts, each message is a section
        elif isinstance(prompt, list) and all(isinstance(m, dict) for m in prompt):
            sections = prompt
            
        # Cannot ablate template objects directly, convert to rendered form
        elif isinstance(prompt, BaseTemplate):
            rendered = prompt.render(**(template_vars or {}))
            if isinstance(rendered, str):
                raw_sections = rendered.split('\n\n')
                sections = [s for s in raw_sections if s.strip()]
            elif isinstance(rendered, list):
                sections = rendered
                
        # Skip ablation if we couldn't identify sections
        if not sections or len(sections) <= 1:
            logger.warning("Cannot perform ablation: prompt cannot be divided into sections")
            return PromptOptimizationResult(
                original_prompt=prompt,
                optimized_prompt=prompt,
                improvement=0.0,
                history=history,
                metrics=initial_metrics,
                strategy=self.strategy,
                runtime_seconds=time.time() - start_time
            )
            
        # Try removing each section and evaluate
        best_prompt = copy.deepcopy(prompt)
        best_score = initial_score
        
        for i in range(len(sections)):
            # Create variation without this section
            if isinstance(prompt, str):
                # For text prompts
                variation = '\n\n'.join(sections[:i] + sections[i+1:])
            elif isinstance(prompt, list):
                # For chat prompts
                variation = sections[:i] + sections[i+1:]
            else:
                # Cannot properly ablate other types
                continue
                
            # Evaluate
            metrics, score = self._evaluate_prompt(variation, reference)
            
            # Add to history
            removed_content = sections[i]
            if isinstance(removed_content, dict):
                removed_content = f"{removed_content.get('role', 'message')}: {removed_content.get('content', '')}"
                
            history.append(PromptVariation(
                prompt=copy.deepcopy(variation),
                description=f"Ablation: removed '{removed_content[:30]}...'",
                metrics=metrics,
                score=score
            ))
            
            # Check if better than current best
            if score >= best_score - self.improvement_threshold:
                best_prompt = copy.deepcopy(variation)
                best_score = score
                logger.info(f"Found simpler prompt with score: {score:.4f}")
                
        runtime = time.time() - start_time
        
        # Final evaluation of best prompt
        final_metrics, _ = self._evaluate_prompt(best_prompt, reference)
        
        improvement = best_score - initial_score
        
        return PromptOptimizationResult(
            original_prompt=prompt,
            optimized_prompt=best_prompt,
            improvement=improvement,
            history=history,
            metrics=final_metrics,
            strategy=self.strategy,
            runtime_seconds=runtime
        )
        
    def _add_specificity(self, prompt: Any) -> Any:
        """Add more specific instructions to the prompt"""
        if isinstance(prompt, str):
            specificity_additions = [
                "\n\nPlease be specific and precise in your response.",
                "\n\nProvide detailed explanations with concrete examples.",
                "\n\nInclude relevant facts, figures, or data to support your points.",
                "\n\nBe thorough and cover all important aspects of the topic.",
            ]
            return prompt + random.choice(specificity_additions)
            
        elif isinstance(prompt, list):
            # For chat format, add to the last user message
            new_prompt = copy.deepcopy(prompt)
            for i in reversed(range(len(new_prompt))):
                if new_prompt[i].get("role") == "user":
                    specificity_addition = random.choice([
                        "Please be specific and precise in your response.",
                        "Provide detailed explanations with concrete examples.",
                        "Include relevant facts, figures, or data to support your points.",
                        "Be thorough and cover all important aspects of the topic."
                    ])
                    new_prompt[i]["content"] += f"\n\n{specificity_addition}"
                    break
            return new_prompt
            
        elif isinstance(prompt, PromptTemplate):
            new_template = copy.deepcopy(prompt)
            new_template.template += "\n\nPlease be specific and precise in your response."
            return new_template
            
        elif isinstance(prompt, ChatPromptTemplate):
            new_template = copy.deepcopy(prompt)
            for i in reversed(range(len(new_template.messages))):
                if new_template.messages[i].role == "user":
                    new_template.messages[i].content += "\n\nPlease be specific and precise in your response."
                    break
            return new_template
            
        return prompt
        
    def _add_constraints(self, prompt: Any) -> Any:
        """Add constraints to improve response quality"""
        constraints = [
            "\n\nImportant constraints:\n- Only include verified information\n- Cite your sources when possible\n- If you're uncertain, acknowledge it\n- Focus on answering the question directly",
            "\n\nPlease adhere to the following guidelines:\n1. Be accurate and factual\n2. Don't include speculative information\n3. Stay on topic\n4. Provide a balanced perspective",
            "\n\nGuidelines:\n- Prioritize accuracy over comprehensiveness\n- Acknowledge limitations in your knowledge\n- Maintain objectivity\n- Provide balanced information"
        ]
        
        if isinstance(prompt, str):
            return prompt + random.choice(constraints)
            
        elif isinstance(prompt, list):
            # For chat format
            new_prompt = copy.deepcopy(prompt)
            # Find system message or last user message
            system_idx = None
            last_user_idx = None
            
            for i, msg in enumerate(new_prompt):
                if msg.get("role") == "system":
                    system_idx = i
                if msg.get("role") == "user":
                    last_user_idx = i
                    
            # Prefer adding to system message if it exists
            if system_idx is not None:
                new_prompt[system_idx]["content"] += random.choice(constraints)
            elif last_user_idx is not None:
                new_prompt[last_user_idx]["content"] += random.choice(constraints)
                
            return new_prompt
            
        elif isinstance(prompt, PromptTemplate):
            new_template = copy.deepcopy(prompt)
            new_template.template += random.choice(constraints)
            return new_template
            
        elif isinstance(prompt, ChatPromptTemplate):
            new_template = copy.deepcopy(prompt)
            # Find system message or last user message
            system_idx = None
            last_user_idx = None
            
            for i, msg in enumerate(new_template.messages):
                if msg.role == "system":
                    system_idx = i
                if msg.role == "user":
                    last_user_idx = i
                    
            # Prefer adding to system message if it exists
            if system_idx is not None:
                new_template.messages[system_idx].content += random.choice(constraints)
            elif last_user_idx is not None:
                new_template.messages[last_user_idx].content += random.choice(constraints)
                
            return new_template
            
        return prompt
        
    def _add_examples(self, prompt: Any) -> Any:
        """Add examples of desired output format"""
        examples = [
            "\n\nHere's an example of a good response: [Example: A clear, factual response that directly addresses the question while acknowledging any limitations or uncertainties]",
            "\n\nExample of expected output format:\n- Start with a direct answer\n- Provide supporting evidence\n- Acknowledge limitations\n- End with a brief summary",
            "\n\nFor example, a good response structure would be:\n1. Direct answer to the question\n2. Supporting facts and evidence\n3. Potential limitations or caveats\n4. Brief conclusion"
        ]
        
        # Similar implementation pattern to _add_constraints
        if isinstance(prompt, str):
            return prompt + random.choice(examples)
            
        elif isinstance(prompt, list):
            new_prompt = copy.deepcopy(prompt)
            for i in reversed(range(len(new_prompt))):
                if new_prompt[i].get("role") == "user":
                    new_prompt[i]["content"] += random.choice(examples)
                    break
            return new_prompt
            
        elif isinstance(prompt, PromptTemplate):
            new_template = copy.deepcopy(prompt)
            new_template.template += random.choice(examples)
            return new_template
            
        elif isinstance(prompt, ChatPromptTemplate):
            new_template = copy.deepcopy(prompt)
            for i in reversed(range(len(new_template.messages))):
                if new_template.messages[i].role == "user":
                    new_template.messages[i].content += random.choice(examples)
                    break
            return new_template
            
        return prompt
        
    def _add_context(self, prompt: Any) -> Any:
        """Add contextual information to improve response relevance"""
        contexts = [
            "\n\nPlease consider the following context: This question is being asked in a professional/academic setting where accuracy and thoroughness are valued.",
            "\n\nContext: The audience for this response has a technical background but may not be deeply familiar with the specific terminology.",
            "\n\nAdditional context: This information will be used for educational purposes, so emphasize clarity and provide authoritative information."
        ]
        
        # Similar implementation pattern to _add_constraints
        if isinstance(prompt, str):
            # Add at the beginning of the prompt
            return random.choice(contexts) + "\n\n" + prompt
            
        elif isinstance(prompt, list):
            new_prompt = copy.deepcopy(prompt)
            # Add to system message if exists, otherwise create one
            for i, msg in enumerate(new_prompt):
                if msg.get("role") == "system":
                    new_prompt[i]["content"] = random.choice(contexts) + "\n\n" + msg["content"]
                    return new_prompt
                    
            # No system message found, add one
            new_prompt.insert(0, {
                "role": "system",
                "content": random.choice(contexts)
            })
            return new_prompt
            
        elif isinstance(prompt, PromptTemplate):
            new_template = copy.deepcopy(prompt)
            new_template.template = random.choice(contexts) + "\n\n" + new_template.template
            return new_template
            
        elif isinstance(prompt, ChatPromptTemplate):
            new_template = copy.deepcopy(prompt)
            # Add to system message if exists, otherwise create one
            for i, msg in enumerate(new_template.messages):
                if msg.role == "system":
                    new_template.messages[i].content = random.choice(contexts) + "\n\n" + msg.content
                    return new_template
            
            # No system message, add one at the beginning
            from .template import SystemMessageTemplate
            new_template.messages.insert(0, SystemMessageTemplate(random.choice(contexts)))
            return new_template
            
        return prompt
        
    def _simplify_language(self, prompt: Any) -> Any:
        """Simplify language for better model comprehension"""
        simplification_instruction = "\n\nPlease use clear, simple language in your response. Avoid jargon unless necessary and explain technical terms."
        
        # Similar implementation pattern to _add_specificity
        if isinstance(prompt, str):
            return prompt + simplification_instruction
            
        elif isinstance(prompt, list):
            new_prompt = copy.deepcopy(prompt)
            for i in reversed(range(len(new_prompt))):
                if new_prompt[i].get("role") == "user":
                    new_prompt[i]["content"] += simplification_instruction
                    break
            return new_prompt
            
        elif isinstance(prompt, PromptTemplate):
            new_template = copy.deepcopy(prompt)
            new_template.template += simplification_instruction
            return new_template
            
        elif isinstance(prompt, ChatPromptTemplate):
            new_template = copy.deepcopy(prompt)
            for i in reversed(range(len(new_template.messages))):
                if new_template.messages[i].role == "user":
                    new_template.messages[i].content += simplification_instruction
                    break
            return new_template
            
        return prompt
        
    def _structure_output(self, prompt: Any) -> Any:
        """Add instructions for structured output format"""
        structure_instructions = [
            "\n\nPlease structure your response with clear headings and bullet points where appropriate.",
            "\n\nFormat your response with: 1) A brief summary answer, 2) Key points with explanations, 3) A conclusion",
            "\n\nPlease organize your response with clear sections: Introduction, Main Points, Conclusion"
        ]
        
        # Similar implementation pattern to _add_specificity
        if isinstance(prompt, str):
            return prompt + random.choice(structure_instructions)
            
        elif isinstance(prompt, list):
            new_prompt = copy.deepcopy(prompt)
            for i in reversed(range(len(new_prompt))):
                if new_prompt[i].get("role") == "user":
                    new_prompt[i]["content"] += random.choice(structure_instructions)
                    break
            return new_prompt
            
        elif isinstance(prompt, PromptTemplate):
            new_template = copy.deepcopy(prompt)
            new_template.template += random.choice(structure_instructions)
            return new_template
            
        elif isinstance(prompt, ChatPromptTemplate):
            new_template = copy.deepcopy(prompt)
            for i in reversed(range(len(new_template.messages))):
                if new_template.messages[i].role == "user":
                    new_template.messages[i].content += random.choice(structure_instructions)
                    break
            return new_template
            
        return prompt
        
    def _add_reasoning_steps(self, prompt: Any) -> Any:
        """Add instructions to show reasoning steps"""
        reasoning_instruction = "\n\nPlease explain your reasoning step by step, showing how you arrive at your conclusions."
        
        # Similar implementation pattern to _add_specificity
        if isinstance(prompt, str):
            return prompt + reasoning_instruction
            
        elif isinstance(prompt, list):
            new_prompt = copy.deepcopy(prompt)
            for i in reversed(range(len(new_prompt))):
                if new_prompt[i].get("role") == "user":
                    new_prompt[i]["content"] += reasoning_instruction
                    break
            return new_prompt
            
        elif isinstance(prompt, PromptTemplate):
            new_template = copy.deepcopy(prompt)
            new_template.template += reasoning_instruction
            return new_template
            
        elif isinstance(prompt, ChatPromptTemplate):
            new_template = copy.deepcopy(prompt)
            for i in reversed(range(len(new_template.messages))):
                if new_template.messages[i].role == "user":
                    new_template.messages[i].content += reasoning_instruction
                    break
            return new_template
    
    def optimize(
        self,
        prompt: Union[str, List[Dict[str, str]], BaseTemplate],
        template_vars: Optional[Dict[str, Any]] = None,
        reference: Optional[str] = None,
    ) -> PromptOptimizationResult:
        """
        Optimize a prompt using the selected strategy.
        
        Args:
            prompt: Initial prompt to optimize
            template_vars: Variables for template rendering (if prompt is a template)
            reference: Optional reference text for evaluation
            
        Returns:
            Optimization result with improved prompt
        """
        # Apply strategy
        if self.strategy == OptimizationStrategy.ITERATIVE:
            return self._optimize_iterative(prompt, template_vars, reference)
        elif self.strategy == OptimizationStrategy.ABLATION:
            return self._optimize_ablation(prompt, template_vars, reference)
        elif self.strategy == OptimizationStrategy.EXPANSION:
            # Expansion is similar to iterative but only adds content
            self.strategy = OptimizationStrategy.EXPANSION  # Set strategy explicitly for result
            return self._optimize_iterative(prompt, template_vars, reference)
        else:
            logger.warning(f"Strategy {self.strategy} not yet implemented, falling back to iterative")
            self.strategy = OptimizationStrategy.ITERATIVE
            return self._optimize_iterative(prompt, template_vars, reference)


def optimize_prompt(
    prompt: Union[str, List[Dict[str, str]]],
    model: Any,
    reference: Optional[str] = None,
    optimize_for: str = "factuality",
    max_iterations: int = 5,
) -> Tuple[Union[str, List[Dict[str, str]]], Dict[str, Any]]:
    """
    Convenience function to optimize a prompt.
    
    Args:
        prompt: Text prompt or chat messages to optimize
        model: Model or inference function to use
        reference: Optional reference for evaluation
        optimize_for: Metric to optimize for
        max_iterations: Maximum number of optimization iterations
        
    Returns:
        Tuple of (optimized prompt, metrics)
    """
    optimizer = PromptOptimizer(
        model=model,
        optimize_for=optimize_for,
        max_iterations=max_iterations,
    )
    
    result = optimizer.optimize(prompt, reference=reference)
    
    return result.optimized_prompt, result.metrics