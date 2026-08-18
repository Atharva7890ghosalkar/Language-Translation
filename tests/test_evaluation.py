import pytest
from src.evaluation.metrics import (
    calculate_sentence_bleu,
    calculate_sentence_chrf,
    evaluate_translation,
    calculate_corpus_bleu,
    calculate_corpus_chrf,
    evaluate_corpus,
)


def test_sentence_bleu_identical():
    candidate = "The weather is very pleasant today."
    reference = "The weather is very pleasant today."
    score = calculate_sentence_bleu(candidate, reference)
    assert isinstance(score, float)
    assert score == 100.0


def test_sentence_bleu_similar():
    candidate = "The weather is quite nice today."
    reference = "The weather is very pleasant today."
    score = calculate_sentence_bleu(candidate, reference)
    assert isinstance(score, float)
    assert 0.0 < score < 100.0


def test_sentence_bleu_unrelated():
    candidate = "Cats love drinking fresh milk."
    reference = "Computers compute binary numbers efficiently."
    score = calculate_sentence_bleu(candidate, reference)
    assert isinstance(score, float)
    assert score < 20.0


def test_sentence_bleu_empty_inputs():
    assert calculate_sentence_bleu("", "Reference text") == 0.0
    assert calculate_sentence_bleu("   ", "Reference text") == 0.0
    assert calculate_sentence_bleu("Candidate text", "") == 0.0
    assert calculate_sentence_bleu("Candidate text", "   ") == 0.0
    assert calculate_sentence_bleu("", "") == 0.0


def test_sentence_chrf_identical():
    candidate = "Bonjour tout le monde."
    reference = "Bonjour tout le monde."
    score = calculate_sentence_chrf(candidate, reference)
    assert isinstance(score, float)
    assert score == 100.0


def test_sentence_chrf_similar():
    candidate = "Bonjour le monde."
    reference = "Bonjour tout le monde."
    score = calculate_sentence_chrf(candidate, reference)
    assert isinstance(score, float)
    assert 50.0 < score < 100.0


def test_sentence_chrf_empty_inputs():
    assert calculate_sentence_chrf("", "Reference text") == 0.0
    assert calculate_sentence_chrf("Candidate text", "") == 0.0


def test_evaluate_translation():
    result = evaluate_translation(
        candidate="Hello world",
        reference="Hello world"
    )
    assert isinstance(result, dict)
    assert "bleu" in result
    assert "chrf" in result
    assert result["bleu"] == 100.0
    assert result["chrf"] == 100.0


def test_corpus_bleu_and_chrf():
    hypotheses = [
        "Hello world",
        "The sun is shining brightly",
        "Machine translation is useful"
    ]
    references = [
        "Hello world",
        "The sun is shining brightly",
        "Machine translation is useful"
    ]
    scores = evaluate_corpus(hypotheses, references)
    assert isinstance(scores, dict)
    assert "corpus_bleu" in scores
    assert "corpus_chrf" in scores
    assert scores["corpus_bleu"] == 100.0
    assert scores["corpus_chrf"] == 100.0


def test_corpus_empty():
    assert calculate_corpus_bleu([], []) == 0.0
    assert calculate_corpus_chrf([], []) == 0.0
