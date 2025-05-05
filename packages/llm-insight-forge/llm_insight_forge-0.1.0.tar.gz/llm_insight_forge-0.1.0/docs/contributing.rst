Contributing
============

Thank you for your interest in contributing to LLM Insight Forge! This document provides guidelines and instructions for contributing to the project.

Development Setup
---------------

To set up the project for development:

1. Clone the repository:

.. code-block:: bash

    git clone https://github.com/biswanathroul/llm-insight-forge.git
    cd llm-insight-forge

2. Create a virtual environment and install development dependencies:

.. code-block:: bash

    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -e ".[dev]"

Code Style
---------

This project follows these coding conventions:

- PEP 8 style guide
- Google-style docstrings
- Type hints for function arguments and return values

We use the following tools to enforce code quality:

- ``black`` for code formatting
- ``isort`` for import sorting
- ``flake8`` for style guide enforcement
- ``mypy`` for static type checking

You can run these tools using:

.. code-block:: bash

    black llm_insight_forge tests
    isort llm_insight_forge tests
    flake8 llm_insight_forge tests
    mypy llm_insight_forge

Testing
------

We use ``pytest`` for testing. To run the tests:

.. code-block:: bash

    pytest

To run tests with coverage:

.. code-block:: bash

    pytest --cov=llm_insight_forge tests/

Pull Request Process
-----------------

1. Fork the repository and create your branch from `main`:

.. code-block:: bash

    git checkout -b feature/your-feature-name

2. Make your changes and ensure the code passes all tests and style checks.

3. Update documentation as needed.

4. Add or update tests to cover your changes.

5. Submit your pull request with a clear description of the changes.

Documentation
-----------

To build the documentation locally:

.. code-block:: bash

    cd docs
    make html

The generated documentation will be in the ``docs/_build/html`` directory.

Adding a New Feature
-----------------

When adding a new feature, please follow these steps:

1. Create a new branch for your feature.

2. Implement the feature with appropriate documentation and tests.

3. Update the relevant documentation files in the ``docs/`` directory.

4. Add an example to the ``examples/`` directory if applicable.

5. Submit a pull request.

Issue Reporting
------------

If you find a bug or want to request a feature, please open an issue on GitHub:

- For bugs, include steps to reproduce, expected behavior, and actual behavior.
- For feature requests, describe the feature and why it would be valuable.

License
------

By contributing to this project, you agree that your contributions will be licensed under the project's MIT License.