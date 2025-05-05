from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="llm_insight_forge",
    version="0.1.0",
    author="Biswanath Roul",
    description="A comprehensive toolkit for LLM evaluation, prompt engineering, fine-tuning, and inference optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/biswanathroul/llm_insight_forge",
    project_urls={
        "Bug Tracker": "https://github.com/biswanathroul/llm_insight_forge/issues",
        "Documentation": "https://llm-insight-forge.readthedocs.io/",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
    ],
    packages=find_packages(include=["llm_insight_forge", "llm_insight_forge.*"]),
    python_requires=">=3.8",
    install_requires=[
        "torch>=1.10.0",
        "transformers>=4.20.0",
        "numpy>=1.19.0",
        "scikit-learn>=1.0.0",
        "nltk>=3.6.0",
        "rouge-score>=0.1.0",
        "datasets>=2.0.0",
        "tqdm>=4.62.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=4.0.0",
            "mypy>=0.940",
        ],
        "docs": [
            "sphinx>=4.4.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.18.0",
        ],
    },
)