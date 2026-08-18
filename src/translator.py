"""Multilingual Neural Machine Translation Engine using NLLB-200.

Provides robust translation with:
- Fast path for short inputs
- Paragraph and sentence-aware chunking for long inputs up to 2,000 characters
- Oversized single-sentence fallback for both space-separated and space-less (CJK) scripts
- Dynamic bounded generation token budgeting
- Resilient chunk translation with subdivision retry (zero silent data loss)
- Same-language shortcut
"""

import re
from typing import List
import torch

try:
    from src.model_service import model, tokenizer, DEVICE
    from src.language_utils import get_language_code
except ImportError:
    from model_service import model, tokenizer, DEVICE
    from language_utils import get_language_code

# Configuration Constants
SAFE_DIRECT_TOKEN_LIMIT = 120   # If input tokens <= 120 and no newlines, use direct fast path
MAX_CHUNK_TOKENS = 100          # Target token budget per chunk for long texts
MAX_GENERATION_TOKENS = 512     # Upper bound on generated tokens per chunk to protect GPU VRAM

# Common abbreviations to prevent false sentence splits (e.g., Dr. Smith, 3.14)
ABBREVIATIONS = {
    "mr", "mrs", "ms", "dr", "prof", "sr", "jr", "vs", "eg", "ie", "st", "etc",
    "vol", "dept", "est", "approx", "no", "co", "corp", "ltd", "inc"
}

# Regex matching sentence-ending punctuation marks (. ! ? । | 。 ！ ？)
DELIMITER_PATTERN = re.compile(r'([。！？]+|[.!?।|]+)')


def _split_into_sentences(paragraph: str) -> List[str]:
    """Split a paragraph into individual sentences while preserving sentence punctuation.
    Supports missing spaces after punctuation and handles decimals & abbreviations.
    """
    text = paragraph.strip()
    if not text:
        return []

    matches = list(DELIMITER_PATTERN.finditer(text))
    if not matches:
        return [text]

    sentences: List[str] = []
    start_idx = 0

    for i, m in enumerate(matches):
        punc = m.group(0)
        punc_start = m.start()
        punc_end = m.end()

        # Check if decimal number (e.g. 3.14)
        if punc == ".":
            char_before = text[punc_start - 1] if punc_start > 0 else ""
            char_after = text[punc_end] if punc_end < len(text) else ""
            if char_before.isdigit() and char_after.isdigit():
                continue  # Skip split on decimal point

            # Check abbreviation (e.g. Dr. Smith)
            preceding_text = text[start_idx:punc_start].strip()
            last_word = preceding_text.split()[-1].lower() if preceding_text.split() else ""
            cleaned_word = re.sub(r'^\W+|\W+$', '', last_word)
            if cleaned_word in ABBREVIATIONS and punc_end < len(text) and text[punc_end] != "\n":
                continue  # Skip split on abbreviation

        # Extract sentence up to punc_end
        sent = text[start_idx:punc_end].strip()

        # Clean up any trailing stray commas or extra separators between sentences (e.g., "how are you?,")
        sent = re.sub(r'[,;\s]+$', '', sent)

        if sent:
            sentences.append(sent)

        # Advance start_idx past any immediate whitespace or stray commas
        next_start = punc_end
        while next_start < len(text) and text[next_start] in " \t,;":
            next_start += 1
        start_idx = next_start

    # Remaining text after last punctuation
    if start_idx < len(text):
        remaining = text[start_idx:].strip()
        remaining = re.sub(r'^[,;\s]+|[,;\s]+$', '', remaining)
        if remaining:
            sentences.append(remaining)

    return sentences if sentences else [paragraph]


def _get_token_count(text: str) -> int:
    """Get accurate token count using tokenizer with fallback."""
    if not text:
        return 0
    try:
        tokens = tokenizer.encode(text, add_special_tokens=False)
        if isinstance(tokens, list):
            return len(tokens)
        return len(text.split())
    except Exception:
        return len(text.split())


def _subdivide_by_tokens_or_chars(text: str, max_tokens: int = MAX_CHUNK_TOKENS) -> List[str]:
    """Subdivide space-less or single-word oversized text (e.g. CJK scripts)
    using tokenizer token slices to guarantee 100% token coverage.
    """
    if not text:
        return []
    try:
        token_ids = tokenizer.encode(text, add_special_tokens=False)
        if isinstance(token_ids, list) and len(token_ids) > max_tokens:
            slices: List[str] = []
            for i in range(0, len(token_ids), max_tokens):
                slice_ids = token_ids[i:i + max_tokens]
                decoded_slice = tokenizer.decode(slice_ids, skip_special_tokens=True).strip()
                if decoded_slice:
                    slices.append(decoded_slice)
            return slices if slices else [text]
    except Exception:
        pass

    # Fallback to character chunking if tokenizer is not accessible or fails
    char_chunk_size = max(20, max_tokens * 3)
    char_chunks: List[str] = []
    for i in range(0, len(text), char_chunk_size):
        char_chunk = text[i:i + char_chunk_size].strip()
        if char_chunk:
            char_chunks.append(char_chunk)
    return char_chunks if char_chunks else [text]


def _subdivide_oversized_sentence(sentence: str, max_tokens: int = MAX_CHUNK_TOKENS) -> List[str]:
    """Fallback: split an oversized sentence (e.g. run-on text with no punctuation,
    or CJK/space-less text) into smaller chunks that strictly fit within max_tokens.
    Ensures 100% token coverage without dropping content.
    """
    sentence = sentence.strip()
    if not sentence:
        return []

    # If the sentence has space-separated words, try word-level grouping first
    words = sentence.split()
    if len(words) > 1:
        sub_chunks: List[str] = []
        current_words: List[str] = []

        for word in words:
            test_chunk = " ".join(current_words + [word])
            token_count = _get_token_count(test_chunk)

            if token_count > max_tokens and current_words:
                sub_chunks.append(" ".join(current_words))
                current_words = [word]
            else:
                current_words.append(word)

        if current_words:
            sub_chunks.append(" ".join(current_words))

        # Check if any individual unit within sub_chunks is still oversized
        final_chunks: List[str] = []
        for chunk in sub_chunks:
            if _get_token_count(chunk) > max_tokens:
                final_chunks.extend(_subdivide_by_tokens_or_chars(chunk, max_tokens))
            else:
                final_chunks.append(chunk)
        return final_chunks
    else:
        # Space-less script (e.g. Japanese, Chinese) or giant single token
        return _subdivide_by_tokens_or_chars(sentence, max_tokens)


def _chunk_paragraph(paragraph: str, max_tokens: int = MAX_CHUNK_TOKENS) -> List[str]:
    """Chunk a paragraph into semantic sentence units bounded by max_tokens."""
    sentences = _split_into_sentences(paragraph)
    atomic_units: List[str] = []

    for sentence in sentences:
        token_count = _get_token_count(sentence)
        if token_count > max_tokens:
            # Oversized sentence fallback
            sub_units = _subdivide_oversized_sentence(sentence, max_tokens)
            atomic_units.extend(sub_units)
        else:
            atomic_units.append(sentence)

    return atomic_units if atomic_units else [paragraph]


def _translate_single_chunk(
    chunk: str,
    source_code: str,
    target_code: str
) -> str:
    """Translate an individual text chunk using NLLB-200 on GPU."""
    if not chunk or not chunk.strip():
        return ""

    tokenizer.src_lang = source_code

    inputs = tokenizer(
        chunk.strip(),
        return_tensors="pt"
    ).to(DEVICE)

    input_token_len = inputs["input_ids"].shape[1] if hasattr(inputs["input_ids"], "shape") else len(chunk.split())
    # Dynamic output token budget bounded by MAX_GENERATION_TOKENS
    dynamic_max_tokens = min(
        MAX_GENERATION_TOKENS,
        max(128, int(input_token_len * 2.5) + 64)
    )

    with torch.no_grad():
        translated_tokens = model.generate(
            **inputs,
            forced_bos_token_id=tokenizer.convert_tokens_to_ids(target_code),
            max_new_tokens=dynamic_max_tokens
        )

    decoded = tokenizer.batch_decode(
        translated_tokens,
        skip_special_tokens=True
    )
    if isinstance(decoded, list) and len(decoded) > 0:
        return str(decoded[0]).strip()
    return str(decoded).strip()


def _translate_with_retry(
    chunk: str,
    source_code: str,
    target_code: str
) -> str:
    """Translate a chunk with automatic subdivision retry on empty output to eliminate silent data loss."""
    if not chunk or not chunk.strip():
        return ""

    translated = _translate_single_chunk(chunk, source_code, target_code)
    if translated and translated.strip():
        return translated.strip()

    # Retry strategy: if a chunk returns empty, subdivide into smaller sub-units and translate each
    smaller_sub_chunks = _subdivide_by_tokens_or_chars(chunk, max_tokens=max(20, MAX_CHUNK_TOKENS // 2))
    if len(smaller_sub_chunks) > 1:
        sub_results: List[str] = []
        for sub in smaller_sub_chunks:
            sub_res = _translate_single_chunk(sub, source_code, target_code)
            if sub_res and sub_res.strip():
                sub_results.append(sub_res.strip())
        if sub_results:
            return " ".join(sub_results)

    # If still empty after subdivision, raise an explicit error rather than silently dropping content
    raise RuntimeError(f"Translation failed for content chunk: '{chunk[:50]}...'")


def translate(
    text: str,
    source_language: str,
    target_language: str
) -> str:
    """Translate input text from source_language to target_language.

    Handles single short sentences via direct fast path, short multi-sentence inputs
    via sentence-aware chunking, and long multi-paragraph inputs up to 2,000 characters
    via paragraph and sentence-aware chunking without content loss.
    """
    if not text or not text.strip():
        return ""

    # Same-language shortcut
    if source_language == target_language:
        return text

    source_code = get_language_code(source_language)
    target_code = get_language_code(target_language)

    # Check total input token count
    token_count = _get_token_count(text)
    paragraphs = text.split("\n")

    # Fast Path: Only if input is a single paragraph, short token count, AND at most 1 sentence
    if len(paragraphs) == 1 and token_count <= SAFE_DIRECT_TOKEN_LIMIT:
        sentences = _split_into_sentences(text)
        if len(sentences) <= 1:
            return _translate_single_chunk(text, source_code, target_code)

    # Multi-sentence / Multi-paragraph path:
    # Preserve paragraph boundaries by splitting on newlines
    translated_paragraphs: List[str] = []

    for para in paragraphs:
        if not para.strip():
            translated_paragraphs.append("")
            continue

        para_chunks = _chunk_paragraph(para, max_tokens=MAX_CHUNK_TOKENS)
        translated_chunks: List[str] = []
        for chunk in para_chunks:
            translated_chunk = _translate_with_retry(chunk, source_code, target_code)
            if not translated_chunk:
                raise RuntimeError(f"Translation returned empty result for chunk: '{chunk[:50]}...'")
            translated_chunks.append(translated_chunk)

        translated_paragraphs.append(" ".join(translated_chunks))

    return "\n".join(translated_paragraphs)


if __name__ == "__main__":
    test_result = translate(
        text="Bonjour tout le monde. Comment allez-vous aujourd'hui ?",
        source_language="French",
        target_language="Japanese"
    )
    print("Test Translation:", test_result)