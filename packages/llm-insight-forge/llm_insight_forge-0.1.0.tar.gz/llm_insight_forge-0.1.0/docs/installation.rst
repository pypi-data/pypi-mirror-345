Installation
============

LLM Insight Forge is available on PyPI and can be installed via pip:

.. code-block:: bash

    pip install llm-insight-forge

Requirements
-----------

LLM Insight Forge requires Python 3.8 or later.

Core dependencies will be installed automatically with the package, including:

* torch
* transformers
* numpy
* scikit-learn
* nltk
* rouge-score
* datasets
* tqdm

Optional Dependencies
-------------------

For specific functionality, you may want to install these optional dependencies:

Fine-tuning:

.. code-block:: bash

    pip install llm-insight-forge[fine-tuning]

This will additionally install:

* peft
* accelerate
* bitsandbytes

Quantization:

.. code-block:: bash

    pip install llm-insight-forge[quantization]

This will additionally install:

* bitsandbytes
* optimum

Development:

.. code-block:: bash

    pip install llm-insight-forge[dev]

This will additionally install:

* pytest
* pytest-cov
* black
* isort
* flake8
* mypy

Documentation:

.. code-block:: bash

    pip install llm-insight-forge[docs]

This will additionally install:

* sphinx
* sphinx-rtd-theme
* myst-parser

From Source
----------

To install the latest development version from the GitHub repository:

.. code-block:: bash

    git clone https://github.com/biswanathroul/llm-insight-forge.git
    cd llm-insight-forge
    pip install -e .