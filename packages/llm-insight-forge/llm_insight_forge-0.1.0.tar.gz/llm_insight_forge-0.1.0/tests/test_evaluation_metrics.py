"""
Tests for the evaluation metrics module.
"""
import pytest
import numpy as np
from llm_insight_forge.evaluation.metrics import (
    calculate_bleu,
    calculate_rouge,
    semantic_similarity,
    factuality_score,
    hallucination_detection,
    bias_detection,
    coherence_score,
)


class TestBleuScore:
    def test_perfect_match(self):
        reference = "This is a test sentence."
        candidate = "This is a test sentence."
        score = calculate_bleu(reference, candidate)
        assert score > 0.99  # Should be nearly 1 for identical sentences
    
    def test_partial_match(self):
        reference = "The quick brown fox jumps over the lazy dog."
        candidate = "A quick brown fox jumps over a lazy dog."
        score = calculate_bleu(reference, candidate)
        assert 0 < score < 1  # Should be between 0 and 1
        
    def test_no_match(self):
        reference = "This is a test sentence."
        candidate = "Something completely different and unrelated."
        score = calculate_bleu(reference, candidate)
        assert score < 0.1  # Should be very low
        
    def test_multiple_references(self):
        references = [
            "The quick brown fox jumps over the lazy dog.",
            "A swift brown fox leaps over the sleepy dog."
        ]
        candidate = "The brown fox jumps over the lazy dog."
        score = calculate_bleu(references, candidate)
        assert 0 < score <= 1


class TestRougeScore:
    def test_perfect_match(self):
        reference = "This is a test sentence."
        candidate = "This is a test sentence."
        scores = calculate_rouge(reference, candidate)
        assert scores["rouge1"]["fmeasure"] > 0.99
        assert scores["rouge2"]["fmeasure"] > 0.99
        assert scores["rougeL"]["fmeasure"] > 0.99
        
    def test_partial_match(self):
        reference = "The quick brown fox jumps over the lazy dog."
        candidate = "A quick brown fox jumps over a lazy dog."
        scores = calculate_rouge(reference, candidate)
        assert 0 < scores["rouge1"]["fmeasure"] < 1
        assert 0 < scores["rougeL"]["fmeasure"] < 1
    
    def test_return_keys(self):
        reference = "This is a test sentence."
        candidate = "This is another sentence."
        scores = calculate_rouge(reference, candidate)
        assert "rouge1" in scores
        assert "rouge2" in scores
        assert "rougeL" in scores
        for rouge_type in ["rouge1", "rouge2", "rougeL"]:
            assert "precision" in scores[rouge_type]
            assert "recall" in scores[rouge_type]
            assert "fmeasure" in scores[rouge_type]


class TestSemanticSimilarity:
    # Note: This test may be skipped in CI environments due to model downloads
    @pytest.mark.skipif(not pytest.importorskip("torch").cuda.is_available(),
                       reason="Skip semantic similarity tests when GPU not available")
    def test_high_similarity(self):
        text1 = "The cat sat on the mat."
        text2 = "A cat was sitting on a mat."
        similarity = semantic_similarity(text1, text2)
        assert 0.7 < similarity <= 1.0
    
    @pytest.mark.skipif(not pytest.importorskip("torch").cuda.is_available(), 
                       reason="Skip semantic similarity tests when GPU not available")
    def test_low_similarity(self):
        text1 = "The cat sat on the mat."
        text2 = "The stock market fell sharply today."
        similarity = semantic_similarity(text1, text2)
        assert 0 <= similarity < 0.5


class TestFactualityScore:
    def test_high_factuality(self):
        reference = "Paris is the capital of France."
        response = "Paris is the capital city of France."
        score = factuality_score(response, reference)
        assert 0.7 < score <= 1.0
    
    def test_low_factuality(self):
        reference = "Paris is the capital of France."
        response = "London is the capital of France."
        score = factuality_score(response, reference)
        assert 0 <= score < 0.5
        
    def test_list_reference(self):
        reference_facts = [
            "Earth orbits the Sun.",
            "The Moon orbits Earth.",
        ]
        response = "Earth orbits the Sun, which is at the center of our solar system."
        score = factuality_score(response, reference_facts, method="fact_matching")
        assert 0 < score <= 1


class TestHallucination:
    def test_hallucination_detection(self):
        reference = "The Eiffel Tower is located in Paris, France."
        response = "The Eiffel Tower is located in Rome, Italy."
        result = hallucination_detection(response, reference)
        assert "hallucination_detected" in result
        assert "hallucination_score" in result
        assert result["hallucination_detected"] is True
        
    def test_no_hallucination(self):
        reference = "The Eiffel Tower is located in Paris, France."
        response = "The famous Eiffel Tower can be found in Paris, the capital of France."
        result = hallucination_detection(response, reference)
        assert result["hallucination_detected"] is False


class TestBiasDetection:
    def test_gender_bias(self):
        text = "He is a doctor while she is a nurse."
        result = bias_detection(text)
        assert "gender" in result
        assert result["gender"] > 0
        
    def test_minimal_bias(self):
        text = "The scientific method involves hypothesis testing and experimental validation."
        result = bias_detection(text)
        for bias_type in result:
            assert 0 <= result[bias_type] < 0.3


class TestCoherence:
    def test_high_coherence(self):
        text = """Artificial intelligence is advancing rapidly. 
        However, it still faces many challenges. 
        Despite these challenges, researchers continue to make progress.
        In fact, recent breakthroughs have shown impressive results."""
        score = coherence_score(text)
        assert 0.7 < score <= 1.0
    
    def test_low_coherence(self):
        text = "AI good. Very smart. Tomorrow sunshine. Biology cell important."
        score = coherence_score(text)
        assert 0 < score < 0.7