Changelog
=========

Version 0.1.0 (2025-05-05)
-------------------------

Initial release of LLM Insight Forge with the following features:

**Added**

- Evaluation module:
  - Text-based metrics (BLEU, ROUGE)
  - Semantic similarity using embeddings
  - Factuality assessment
  - Hallucination detection
  - Bias detection
  - Coherence scoring

- Prompt Engineering module:
  - Prompt template system with variable substitution
  - Chat-based templates for modern LLMs
  - Few-shot templates with example formatting
  - Prompt optimization techniques
  - Jailbreak detection with multiple detection strategies

- Fine-tuning module:
  - Dataset preparation and formatting utilities
  - Support for supervised fine-tuning
  - Parameter-efficient methods (LoRA)
  - Training configuration management

- Inference Optimization module:
  - Model quantization (INT8, INT4, GPTQ)
  - Batch inference utilities
  - Benchmarking tools

- Examples:
  - Evaluation examples
  - Prompt optimization examples
  - Fine-tuning examples
  - Inference optimization examples

- Documentation:
  - Installation guide
  - Quick start guide
  - API reference
  - Example walkthroughs

Unreleased Changes
----------------

**Added**

- Support for additional quantization methods
- Enhanced benchmark visualization tools
- Fine-tuning with QLoRA technique
- New prompt template types for specialized use cases

**Changed**

- Improved documentation with more examples
- Optimized performance for semantic similarity calculations