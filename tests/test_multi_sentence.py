"""Regression tests for robust multi-sentence translation handling regardless of punctuation and spacing."""

import pytest
from src.translator import translate, _split_into_sentences


def test_sentence_split_logic_variations():
    """Verify sentence boundary detection works with and without space after punctuation."""
    s1 = _split_into_sentences("Hello, how are you? What are you doing?")
    assert len(s1) == 2
    assert s1[0] == "Hello, how are you?"
    assert s1[1] == "What are you doing?"

    s2 = _split_into_sentences("Hello, how are you?What are you doing?")
    assert len(s2) == 2
    assert s2[0] == "Hello, how are you?"
    assert s2[1] == "What are you doing?"

    s3 = _split_into_sentences("Hello, how are you?, what are you doing?")
    assert len(s3) == 2
    assert s3[0] == "Hello, how are you?"
    assert s3[1] == "what are you doing?"

    s4 = _split_into_sentences("Hello!What are you doing?")
    assert len(s4) == 2
    assert s4[0] == "Hello!"
    assert s4[1] == "What are you doing?"

    s5 = _split_into_sentences("Hello. How are you?")
    assert len(s5) == 2
    assert s5[0] == "Hello."
    assert s5[1] == "How are you?"

    s_single = _split_into_sentences("Hello, how are you?")
    assert len(s_single) == 1
    assert s_single[0] == "Hello, how are you?"


def test_multi_sentence_translation_english_to_hindi():
    """Verify both sentences are translated for punctuation and spacing variations."""
    prompts = [
        "Hello, how are you? What are you doing?",
        "Hello, how are you?What are you doing?",
        "Hello, how are you?, what are you doing?",
        "Hello! What are you doing?",
        "Hello!What are you doing?",
    ]

    for text in prompts:
        res = translate(text, "English", "Hindi")
        assert res is not None and len(res.strip()) > 0
        # Verify both sentences translated (contains translated greeting AND question)
        assert ("आप कैसे हैं" in res or "कैसे हैं" in res or "नमस्ते" in res or "हैलो" in res)
        assert ("कर रहे" in res or "क्या कर" in res)


def test_multi_sentence_translation_english_to_french():
    """Verify multi-sentence translation in another language (French)."""
    text = "Hello, how are you?What are you doing?"
    res = translate(text, "English", "French")
    assert res is not None and len(res.strip()) > 0
    assert "Comment allez-vous" in res or "Comment vas-tu" in res or "comment" in res.lower()
    assert "tu fais quoi" in res.lower() or "que fais-tu" in res.lower() or "qu'est-ce que" in res.lower() or "fais" in res.lower()


def test_single_sentence_fast_path():
    """Verify single sentence input works cleanly via direct fast path."""
    res = translate("Hello, how are you?", "English", "Hindi")
    assert res is not None and len(res.strip()) > 0
    assert "आप कैसे हैं" in res or "कैसे हैं" in res or "नमस्ते" in res or "हैलो" in res
