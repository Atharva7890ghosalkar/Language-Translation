"""Model evaluation script for NLLB-200 translation quality.

This script:
1. Loads the manually curated evaluation dataset (data/evaluation/evaluation_set.json).
2. Reuses the existing NLLB-200 GPU model (loaded once via model_service).
3. Generates candidate translations for all benchmark samples.
4. Computes BLEU and chrF metrics per sentence, per language pair, and overall.
5. Prints a structured evaluation report and saves results to evaluation_report.json.
"""

import sys
import json
import time
from pathlib import Path
from collections import defaultdict

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.translator import translate
from src.evaluation.metrics import (
    calculate_sentence_bleu,
    calculate_sentence_chrf,
    calculate_corpus_bleu,
    calculate_corpus_chrf,
)


def load_dataset(dataset_path: Path) -> list[dict]:
    """Load evaluation samples from JSON file."""
    if not dataset_path.exists():
        raise FileNotFoundError(f"Evaluation dataset not found at: {dataset_path}")
    with open(dataset_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_evaluation():
    dataset_path = PROJECT_ROOT / "data" / "evaluation" / "evaluation_set.json"
    report_path = PROJECT_ROOT / "data" / "evaluation" / "evaluation_report.json"

    print("=" * 75)
    print("      NLLB-200 MULTILINGUAL TRANSLATION EVALUATION BENCHMARK")
    print("=" * 75)
    print(f"Loading dataset from: {dataset_path}")
    samples = load_dataset(dataset_path)
    print(f"Loaded {len(samples)} evaluation samples across multiple language pairs.\n")

    print("Generating translations with NLLB-200 on GPU...")
    start_time = time.time()

    evaluated_samples = []
    pair_grouped = defaultdict(list)

    for idx, sample in enumerate(samples, start=1):
        src_lang = sample["source_language"]
        tgt_lang = sample["target_language"]
        src_text = sample["source_text"]
        ref_text = sample["reference_translation"]

        # Run translation through existing NLLB-200 engine
        candidate_text = translate(
            text=src_text,
            source_language=src_lang,
            target_language=tgt_lang
        )

        sent_bleu = calculate_sentence_bleu(candidate_text, ref_text, target_language=tgt_lang)
        sent_chrf = calculate_sentence_chrf(candidate_text, ref_text)

        eval_record = {
            "id": sample.get("id", idx),
            "source_language": src_lang,
            "target_language": tgt_lang,
            "source_text": src_text,
            "reference_translation": ref_text,
            "candidate_translation": candidate_text,
            "sentence_bleu": sent_bleu,
            "sentence_chrf": sent_chrf,
        }

        evaluated_samples.append(eval_record)
        pair_key = f"{src_lang} -> {tgt_lang}"
        pair_grouped[pair_key].append(eval_record)

        print(f"  [{idx}/{len(samples)}] {pair_key} | BLEU: {sent_bleu:5.2f} | chrF: {sent_chrf:5.2f}")

    elapsed_time = time.time() - start_time
    print(f"\nCompleted {len(samples)} translations in {elapsed_time:.2f}s "
          f"({elapsed_time / len(samples):.2f}s/sample)\n")

    # Compute Language-Pair Corpus Metrics
    pair_results = {}
    all_hypotheses = [s["candidate_translation"] for s in evaluated_samples]
    all_references = [s["reference_translation"] for s in evaluated_samples]

    print("=" * 75)
    print("                    PER-LANGUAGE-PAIR RESULTS")
    print("=" * 75)
    print(f"{'Language Pair':<28} | {'Samples':<8} | {'Pair BLEU':<12} | {'Pair chrF':<12}")
    print("-" * 75)

    pair_bleu_scores = []
    pair_chrf_scores = []

    for pair_key, items in pair_grouped.items():
        tgt_lang = items[0]["target_language"]
        hyps = [item["candidate_translation"] for item in items]
        refs = [item["reference_translation"] for item in items]

        pair_bleu = calculate_corpus_bleu(hyps, refs, target_language=tgt_lang)
        pair_chrf = calculate_corpus_chrf(hyps, refs)


        pair_bleu_scores.append(pair_bleu)
        pair_chrf_scores.append(pair_chrf)

        pair_results[pair_key] = {
            "sample_count": len(items),
            "pair_corpus_bleu": pair_bleu,
            "pair_corpus_chrf": pair_chrf,
        }

        print(f"{pair_key:<28} | {len(items):<8} | {pair_bleu:<12.2f} | {pair_chrf:<12.2f}")

    # Compute Overall Metrics
    overall_corpus_bleu = calculate_corpus_bleu(all_hypotheses, all_references)
    overall_corpus_chrf = calculate_corpus_chrf(all_hypotheses, all_references)
    mean_pair_bleu = round(sum(pair_bleu_scores) / len(pair_bleu_scores), 2) if pair_bleu_scores else 0.0
    mean_pair_chrf = round(sum(pair_chrf_scores) / len(pair_chrf_scores), 2) if pair_chrf_scores else 0.0

    print("=" * 75)
    print("                      OVERALL EVALUATION SUMMARY")
    print("=" * 75)
    print(f"Total Evaluation Samples       : {len(samples)}")
    print(f"Total Language Directions      : {len(pair_grouped)}")
    print(f"Overall Corpus BLEU            : {overall_corpus_bleu:.2f}")
    print(f"Overall Corpus chrF            : {overall_corpus_chrf:.2f}")
    print(f"Mean of Language-Pair BLEU     : {mean_pair_bleu:.2f}")
    print(f"Mean of Language-Pair chrF     : {mean_pair_chrf:.2f}")
    print(f"Total GPU Evaluation Time      : {elapsed_time:.2f}s")
    print("=" * 75)

    # Save results to JSON report
    report_data = {
        "metadata": {
            "model": "facebook/nllb-200-distilled-600M",
            "device": "cuda",
            "evaluation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_samples": len(samples),
            "total_pairs": len(pair_grouped),
            "elapsed_seconds": round(elapsed_time, 2)
        },
        "summary": {
            "overall_corpus_bleu": overall_corpus_bleu,
            "overall_corpus_chrf": overall_corpus_chrf,
            "mean_language_pair_bleu": mean_pair_bleu,
            "mean_language_pair_chrf": mean_pair_chrf
        },
        "per_language_pair": pair_results,
        "detailed_samples": evaluated_samples
    }

    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    print(f"\nEvaluation report successfully saved to: {report_path}")
    return report_data


if __name__ == "__main__":
    run_evaluation()
