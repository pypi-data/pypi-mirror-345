"""
Test configuration for LLM Insight Forge.
"""
import os
import pytest
import torch


@pytest.fixture
def reference_text():
    """Sample reference text for testing."""
    return "The Eiffel Tower is a wrought-iron lattice tower located on the Champ de Mars in Paris, France. It was constructed from 1887 to 1889 as the entrance to the 1889 World's Fair."


@pytest.fixture
def response_text():
    """Sample model response text for testing."""
    return "The Eiffel Tower is a famous landmark in Paris, France. It was built in 1889 for the World's Fair and stands at 324 meters tall."


@pytest.fixture
def mock_tokenizer():
    """Mock tokenizer for testing."""
    class MockTokenizer:
        def __call__(self, text, return_tensors="pt", padding=True, truncation=True, max_length=None):
            # Convert text to list of tokens by splitting on spaces (simplified)
            if isinstance(text, str):
                tokens = text.split()
                return {
                    "input_ids": torch.tensor([[i+1 for i in range(len(tokens))]]),
                    "attention_mask": torch.tensor([[1] * len(tokens)])
                }
            elif isinstance(text, list):
                result = {"input_ids": [], "attention_mask": []}
                for item in text:
                    tokens = item.split()
                    result["input_ids"].append([i+1 for i in range(len(tokens))])
                    result["attention_mask"].append([1] * len(tokens))
                return {
                    "input_ids": torch.tensor(result["input_ids"]),
                    "attention_mask": torch.tensor(result["attention_mask"])
                }
            
        def decode(self, token_ids, skip_special_tokens=True):
            # Convert token IDs back to text (simplified)
            return " ".join([f"token{i}" for i in token_ids])
            
        def batch_decode(self, token_ids, skip_special_tokens=True):
            # Batch decode token IDs to texts
            return [self.decode(ids, skip_special_tokens) for ids in token_ids]
    
    return MockTokenizer()


@pytest.fixture
def mock_model():
    """Mock model for testing."""
    class MockModel:
        def __init__(self):
            self.device = torch.device("cpu")
            
        def __call__(self, prompt):
            return {"generated_text": f"Response to: {prompt[:20]}..."}
            
        def generate(self, **kwargs):
            input_ids = kwargs.get("input_ids", torch.tensor([[1, 2, 3]]))
            new_tokens = torch.tensor([[4, 5, 6, 7]])
            return torch.cat([input_ids, new_tokens], dim=1)
            
        def to(self, device):
            return self
            
        def eval(self):
            return self
            
        def parameters(self):
            yield torch.nn.Parameter(torch.randn(10, 10))
    
    return MockModel()


@pytest.fixture
def sample_prompt_template_data():
    """Sample data for testing prompt templates."""
    return {
        "topic": "quantum computing",
        "audience": "a high school student",
        "style": "simple",
        "examples": "Example 1\nExample 2",
        "domain": "computer science",
        "concept": "neural networks",
        "word_limit": 100
    }