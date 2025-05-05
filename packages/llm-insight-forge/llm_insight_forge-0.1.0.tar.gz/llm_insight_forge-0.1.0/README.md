# LLM Insight Forge

A comprehensive toolkit for working with Large Language Models (LLMs), offering advanced capabilities for evaluation, prompt engineering, fine-tuning, and inference optimization.

[![PyPI version](https://badge.fury.io/py/llm-insight-forge.svg)](https://badge.fury.io/py/llm-insight-forge)
[![Python Version](https://img.shields.io/pypi/pyversions/llm-insight-forge.svg)](https://pypi.org/project/llm-insight-forge/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

LLM Insight Forge provides a modular toolkit for various LLM operations:

### 📊 Evaluation

- Text similarity metrics (BLEU, ROUGE)
- Semantic similarity using embeddings
- Factuality assessment
- Hallucination detection
- Bias detection
- Coherence and fluency scoring
- Comprehensive benchmarking

### ✨ Prompt Engineering

- Structured prompt templates
- Prompt optimization techniques
- Jailbreak detection and prevention
- Cross-model prompt compatibility

### 🔧 Fine-Tuning

- Dataset preparation and preprocessing
- Supervised fine-tuning (SFT)
- Parameter-efficient tuning methods (LoRA, P-Tuning, etc.)
- Training job management and monitoring

### ⚡ Inference Optimization

- Model quantization techniques
- Batched inference processing
- Caching strategies
- Hardware-specific optimizations

## Installation

```bash
pip install llm-insight-forge
```

For development:

```bash
pip install llm-insight-forge[dev]
```

For building documentation:

```bash
pip install llm-insight-forge[docs]
```

## Quick Start

```python
import llm_insight_forge as lif

# Evaluate model responses
score = lif.evaluate_response(
    response="The Earth orbits around the Sun in 365.25 days.",
    reference="The Earth completes one orbit around the Sun in approximately 365.25 days.",
    metrics=["bleu", "semantic_similarity", "factuality"]
)
print(f"Evaluation score: {score}")

# Create and optimize prompts
template = lif.PromptTemplate(
    "Answer the following question about {topic}: {question}"
)
prompt = template.format(
    topic="astronomy",
    question="How long does it take for Earth to orbit the Sun?"
)
optimized_prompt = lif.optimize_prompt(prompt, target_model="gpt-4")

# Prepare datasets for fine-tuning
dataset = lif.prepare_dataset(
    data_path="path/to/data.jsonl",
    instruction_field="instruction",
    input_field="input",
    output_field="output"
)

# Train a model
lif.train_model(
    model_name="meta-llama/Llama-2-7b-hf",
    dataset=dataset,
    method="lora",
    output_dir="./fine_tuned_model"
)

# Optimize inference
quantized_model = lif.quantize_model(
    model_path="./fine_tuned_model",
    bits=4
)
```

## Documentation

For comprehensive documentation, visit [our documentation site](https://llm-insight-forge.readthedocs.io/).

## Example Scripts

Check out the `examples/` directory for more usage examples:

- `basic_evaluation.py`: Simple response evaluation workflow
- `advanced_metrics.py`: Using advanced hallucination and bias metrics
- `prompt_optimization.py`: Optimizing prompts for different models
- `fine_tuning_example.py`: Complete fine-tuning workflow
- `inference_optimization.py`: Quantization and batch inference

## Contributing

Contributions are welcome! Please check out our [contributing guidelines](CONTRIBUTING.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use LLM Insight Forge in your research, please cite:

```bibtex
@software{biswanath2025llminsightforge,
  author = {Roul, Biswanath},
  title = {LLM Insight Forge: A Toolkit for LLM Evaluation and Optimization},
  year = {2025},
  url = {https://github.com/biswanathroul/llm_insight_forge}
}
```