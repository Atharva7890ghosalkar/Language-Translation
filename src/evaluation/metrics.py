"""Translation quality evaluation metrics using BLEU and chrF.

This module provides standard sentence-level and corpus-level metric computation
using SacreBLEU, the standard evaluation tool in machine translation.
"""

from typing import Union, List, Dict
import sacrebleu


def _select_tokenizer(target_language: str = None, text: str = None) -> str:
    """Select appropriate SacreBLEU tokenizer.

    Uses 'char' for Japanese, Chinese, Thai or texts containing CJK/non-spaced scripts,
    and standard '13a' for whitespace-delimited scripts.
    """
    if target_language:
        lang_lower = target_language.lower()
        if lang_lower in ["japanese", "chinese", "thai"]:
            return "char"

    if text:
        for ch in text:
            code = ord(ch)
            if (0x4E00 <= code <= 0x9FFF or   # CJK Ideographs
                0x3040 <= code <= 0x309F or   # Hiragana
                0x30A0 <= code <= 0x30FF or   # Katakana
                0x0E00 <= code <= 0x0E7F):    # Thai
                return "char"

    return "13a"


def _normalize_references(reference: Union[str, List[str]]) -> List[str]:
    """Normalize a single reference or list of references to a list of strings."""
    if isinstance(reference, str):
        return [reference.strip()]
    return [ref.strip() for ref in reference if isinstance(ref, str) and ref.strip()]


def calculate_sentence_bleu(
    candidate: str,
    reference: Union[str, List[str]],
    smooth: bool = True,
    target_language: str = None
) -> float:
    """Calculate sentence-level BLEU score (0 - 100).

    Args:
        candidate: The model generated hypothesis translation.
        reference: Ground truth reference translation(s).
        smooth: Whether to use exponential smoothing for short sentences.
        target_language: Optional target language name for script-aware tokenization.

    Returns:
        float: BLEU score between 0.0 and 100.0 rounded to 2 decimal places.
    """
    if not candidate or not candidate.strip():
        return 0.0

    refs = _normalize_references(reference)
    if not refs:
        return 0.0

    smooth_method = "exp" if smooth else "none"
    tokenizer = _select_tokenizer(target_language, candidate or refs[0])

    try:
        bleu = sacrebleu.sentence_bleu(
            candidate.strip(),
            refs,
            smooth_method=smooth_method,
            tokenize=tokenizer
        )
        return round(float(bleu.score), 2)
    except Exception:
        return 0.0



def calculate_sentence_chrf(
    candidate: str,
    reference: Union[str, List[str]]
) -> float:
    """Calculate sentence-level chrF score (0 - 100).

    chrF evaluates character n-gram F-score, making it effective for
    morphologically rich languages and character-based scripts (CJK, Indic).

    Args:
        candidate: The model generated hypothesis translation.
        reference: Ground truth reference translation(s).

    Returns:
        float: chrF score between 0.0 and 100.0 rounded to 2 decimal places.
    """
    if not candidate or not candidate.strip():
        return 0.0

    refs = _normalize_references(reference)
    if not refs:
        return 0.0

    try:
        chrf = sacrebleu.sentence_chrf(
            candidate.strip(),
            refs
        )
        return round(float(chrf.score), 2)
    except Exception:
        return 0.0


def evaluate_translation(
    candidate: str,
    reference: Union[str, List[str]],
    target_language: str = None
) -> Dict[str, float]:
    """Calculate both sentence-level BLEU and chrF scores for a translation.

    Args:
        candidate: The model generated hypothesis translation.
        reference: Ground truth reference translation(s).
        target_language: Optional target language name.

    Returns:
        dict: {"bleu": float, "chrf": float}
    """
    return {
        "bleu": calculate_sentence_bleu(candidate, reference, target_language=target_language),
        "chrf": calculate_sentence_chrf(candidate, reference),
    }



def _format_corpus_references(
    references: Union[List[str], List[List[str]]]
) -> List[List[str]]:
    """Format references into the structure expected by sacrebleu.corpus_bleu.

    SacreBLEU expects a list of reference streams: [[ref1_doc1, ref1_doc2], [ref2_doc1, ...]].
    """
    if not references:
        return []

    # If passed a list of strings [ref1, ref2, ref3]
    if isinstance(references[0], str):
        return [[r.strip() for r in references]]  # type: ignore

    # If passed a list of reference lists [[ref1_a, ref1_b], [ref2_a, ref2_b]]
    # Transpose into streams
    max_refs = max(len(ref_list) for ref_list in references)
    streams: List[List[str]] = [[] for _ in range(max_refs)]
    for ref_list in references:
        for stream_idx in range(max_refs):
            if stream_idx < len(ref_list):
                streams[stream_idx].append(ref_list[stream_idx].strip())
            else:
                # If variable number of references, pad with first reference
                streams[stream_idx].append(ref_list[0].strip() if ref_list else "")

    return streams


def calculate_corpus_bleu(
    hypotheses: List[str],
    references: Union[List[str], List[List[str]]],
    target_language: str = None
) -> float:
    """Calculate standard corpus-level BLEU score (0 - 100).

    Args:
        hypotheses: List of candidate translations.
        references: List of reference translations (1 per hypothesis or multiple per hypothesis).
        target_language: Optional target language name for script-aware tokenization.

    Returns:
        float: Corpus BLEU score between 0.0 and 100.0 rounded to 2 decimal places.
    """
    if not hypotheses or not references:
        return 0.0

    cleaned_hyps = [h.strip() if isinstance(h, str) else "" for h in hypotheses]
    ref_streams = _format_corpus_references(references)

    sample_text = cleaned_hyps[0] if cleaned_hyps else (ref_streams[0][0] if ref_streams and ref_streams[0] else None)
    tokenizer = _select_tokenizer(target_language, sample_text)

    try:
        bleu = sacrebleu.corpus_bleu(cleaned_hyps, ref_streams, tokenize=tokenizer)
        return round(float(bleu.score), 2)
    except Exception:
        return 0.0



def calculate_corpus_chrf(
    hypotheses: List[str],
    references: Union[List[str], List[List[str]]]
) -> float:
    """Calculate standard corpus-level chrF score (0 - 100).

    Args:
        hypotheses: List of candidate translations.
        references: List of reference translations.

    Returns:
        float: Corpus chrF score between 0.0 and 100.0 rounded to 2 decimal places.
    """
    if not hypotheses or not references:
        return 0.0

    cleaned_hyps = [h.strip() if isinstance(h, str) else "" for h in hypotheses]
    ref_streams = _format_corpus_references(references)

    try:
        chrf = sacrebleu.corpus_chrf(cleaned_hyps, ref_streams)
        return round(float(chrf.score), 2)
    except Exception:
        return 0.0


def evaluate_corpus(
    hypotheses: List[str],
    references: Union[List[str], List[List[str]]],
    target_language: str = None
) -> Dict[str, float]:
    """Calculate standard corpus-level BLEU and chrF scores across multiple translations.

    Args:
        hypotheses: List of candidate translations.
        references: List of reference translations.
        target_language: Optional target language name.

    Returns:
        dict: {"corpus_bleu": float, "corpus_chrf": float}
    """
    return {
        "corpus_bleu": calculate_corpus_bleu(hypotheses, references, target_language=target_language),
        "corpus_chrf": calculate_corpus_chrf(hypotheses, references),
    }

