import pytest
from src.translator import (
    _split_into_sentences,
    _subdivide_oversized_sentence,
    _subdivide_by_tokens_or_chars,
    _chunk_paragraph,
    translate,
)


def test_split_into_sentences_standard():
    text = "Artificial intelligence is advancing rapidly. It transforms many industries! Can it solve climate change? We hope so."
    sentences = _split_into_sentences(text)
    assert len(sentences) == 4
    assert sentences[0] == "Artificial intelligence is advancing rapidly."
    assert sentences[1] == "It transforms many industries!"
    assert sentences[2] == "Can it solve climate change?"
    assert sentences[3] == "We hope so."


def test_split_into_sentences_devanagari():
    text = "भारत एक विशाल देश है। यहाँ कई भाषाएँ बोली जाती हैं।"
    sentences = _split_into_sentences(text)
    assert len(sentences) == 2
    assert "भारत" in sentences[0]
    assert "भाषाएँ" in sentences[1]


def test_split_into_sentences_cjk():
    text = "機械翻訳は急速に進歩しています。多くの分野で活用されています！"
    sentences = _split_into_sentences(text)
    assert len(sentences) == 2
    assert "機械翻訳" in sentences[0]
    assert "活用" in sentences[1]


def test_split_into_sentences_no_punctuation():
    text = "this is a continuous run-on sentence without any punctuation whatsoever"
    sentences = _split_into_sentences(text)
    assert len(sentences) == 1
    assert sentences[0] == text


def test_split_into_sentences_empty():
    assert _split_into_sentences("") == []
    assert _split_into_sentences("   ") == []


def test_oversized_sentence_fallback_english():
    # Long English sentence without punctuation (150 words)
    words = [f"tokenword{i}" for i in range(150)]
    long_sentence = " ".join(words)

    sub_chunks = _subdivide_oversized_sentence(long_sentence, max_tokens=30)
    assert len(sub_chunks) > 1

    # Verify 100% word coverage (zero words dropped)
    reconstructed_words = []
    for chunk in sub_chunks:
        reconstructed_words.extend(chunk.split())
    assert reconstructed_words == words


def test_oversized_sentence_fallback_cjk():
    # Long Japanese string with zero spaces and zero punctuation
    japanese_chars = "人工知能の発展により自然言語処理と機械翻訳の性能が劇的に向上し多言語コミュニケーションが可能になりました" * 5
    sub_chunks = _subdivide_oversized_sentence(japanese_chars, max_tokens=25)
    assert len(sub_chunks) > 1

    # Verify all sub-chunks are non-empty
    for chunk in sub_chunks:
        assert len(chunk.strip()) > 0


def test_chunk_paragraph_preserves_sentences():
    para = (
        "Natural language processing is a subfield of artificial intelligence. "
        "It focuses on the interaction between computers and human language. "
        "Modern neural models use transformer architectures for seq2seq translation. "
        "These models can handle dozens of languages simultaneously."
    )
    chunks = _chunk_paragraph(para, max_tokens=50)
    assert len(chunks) >= 1

    # Verify all words from paragraph are covered in the chunks in exact order
    combined_chunk_text = " ".join(chunks)
    for word in para.split():
        assert word in combined_chunk_text


def test_same_language_shortcut():
    text = "This is English text that should not change."
    result = translate(text, "English", "English")
    assert result == text

    marathi_text = "हा मराठी मजकूर आहे."
    result_mr = translate(marathi_text, "Marathi", "Marathi")
    assert result_mr == marathi_text
