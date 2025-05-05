Examples
========

LLM Insight Forge comes with several example scripts that demonstrate how to use the library for common tasks. These examples are located in the ``examples/`` directory of the package.

Evaluation Examples
-----------------

The ``evaluation_example.py`` script demonstrates various methods for evaluating LLM responses:

.. code-block:: bash

    python examples/evaluation_example.py --demo all

This will run demonstrations for:

- Single response evaluation with multiple metrics
- Batch evaluation of multiple responses
- In-depth factuality assessment

You can also run specific demos:

.. code-block:: bash

    python examples/evaluation_example.py --demo single
    python examples/evaluation_example.py --demo batch
    python examples/evaluation_example.py --demo factuality

Prompt Engineering Examples
------------------------

The ``prompt_optimization.py`` script demonstrates the prompt engineering capabilities:

.. code-block:: bash

    python examples/prompt_optimization.py --demo all

This will run demonstrations for:

- Creating and using prompt templates
- Optimizing prompts for better performance
- Detecting jailbreak attempts

You can also run specific demos:

.. code-block:: bash

    python examples/prompt_optimization.py --demo templates
    python examples/prompt_optimization.py --demo optimization
    python examples/prompt_optimization.py --demo jailbreak

Inference Optimization Examples
----------------------------

The ``inference_optimization.py`` script demonstrates model quantization for faster inference:

.. code-block:: bash

    python examples/inference_optimization.py --model facebook/opt-125m --method bnb_4bit

This will:

1. Load the specified model
2. Quantize it using the specified method
3. Run benchmark comparisons between the original and quantized model

Fine-tuning Examples
-----------------

The ``fine_tuning_example.py`` script demonstrates how to fine-tune models:

.. code-block:: bash

    python examples/fine_tuning_example.py --model facebook/opt-125m

This will:

1. Create a sample instruction dataset
2. Format and tokenize the data
3. Set up a LoRA-based fine-tuning configuration
4. Demonstrate the fine-tuning process (without actually training to save resources)

Custom Examples
-------------

The examples are designed to be easily adaptable for your specific use cases. Here are some ways to customize them:

Using Your Own Models
~~~~~~~~~~~~~~~~~~~

To use your own models with the examples, simply provide the model path:

.. code-block:: bash

    python examples/inference_optimization.py --model /path/to/your/model

Using Your Own Datasets
~~~~~~~~~~~~~~~~~~~~~

For fine-tuning with your own datasets:

.. code-block:: bash

    python examples/fine_tuning_example.py --model facebook/opt-125m --dataset /path/to/your/data.jsonl

For more detailed information on customizing the examples, refer to the comments in the example files themselves.