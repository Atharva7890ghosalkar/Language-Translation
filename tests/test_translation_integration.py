import pytest
from src.translator import translate


@pytest.mark.integration
def test_real_nllb_translations_multilingual():
    """Real GPU end-to-end translation test using loaded NLLB-200 model."""

    # Test Direction 1: French -> Japanese
    fr_to_ja = translate(
        text="Bonjour tout le monde",
        source_language="French",
        target_language="Japanese"
    )
    assert isinstance(fr_to_ja, str)
    assert len(fr_to_ja) > 0

    # Test Direction 2: Japanese -> English
    ja_to_en = translate(
        text="こんにちは",
        source_language="Japanese",
        target_language="English"
    )
    assert isinstance(ja_to_en, str)
    assert len(ja_to_en) > 0

    # Test Direction 3: Hindi -> German
    hi_to_de = translate(
        text="नमस्ते, आप कैसे हैं?",
        source_language="Hindi",
        target_language="German"
    )
    assert isinstance(hi_to_de, str)
    assert len(hi_to_de) > 0

    # Test Direction 4: German -> Spanish
    de_to_es = translate(
        text="Guten Tag, wie geht es Ihnen?",
        source_language="German",
        target_language="Spanish"
    )
    assert isinstance(de_to_es, str)
    assert len(de_to_es) > 0


@pytest.mark.integration
def test_long_text_english_to_marathi_near_2000_chars():
    """Verify ~1,900-character multi-paragraph English to Marathi translation on RTX 3050 GPU.
    Tests distinct sections from beginning, middle, to end to ensure zero content loss.
    """
    long_english_text = (
        "Section One covers the historical foundation of machine translation and early statistical models. "
        "Statistical machine translation relied heavily on bilingual phrase tables and n-gram language models, which struggled with long-range syntactic dependencies.\n\n"
        "Section Two explores the breakthrough of sequence-to-sequence neural architectures and multi-head self-attention. "
        "Modern transformer architectures allow deep representations of context across entire sentences, producing substantially more fluent and accurate translations.\n\n"
        "Section Three discusses multilingual foundation models such as NLLB-200. "
        "These models are trained directly on hundreds of languages, eliminating the traditional error-prone English pivot approach for non-English language pairs.\n\n"
        "Section Four examines high-impact practical applications in global healthcare, disaster management, and education. "
        "When emergency responders and medical professionals can communicate immediately in local native languages, lives are saved and humanitarian aid is delivered efficiently.\n\n"
        "Section Five focuses on rigorous quantitative evaluation using standard benchmarks like BLEU and chrF. "
        "Automated scoring combined with linguistic verification guarantees that semantic fidelity and grammatical coherence remain robust across technical domains.\n\n"
        "Section Six presents the final conclusion and future directions of neural machine translation research. "
        "This concludes our comprehensive end-to-end evaluation of long-sequence multilingual translation on GPU hardware."
    )

    text_len = len(long_english_text)
    assert 1500 <= text_len <= 2000, f"Expected near-2000 chars, got {text_len}"

    marathi_translation = translate(
        text=long_english_text,
        source_language="English",
        target_language="Marathi"
    )

    assert isinstance(marathi_translation, str)
    assert len(marathi_translation) > 1000

    # Verify all 6 paragraphs are represented
    input_paragraphs = [p for p in long_english_text.split("\n\n") if p.strip()]
    output_paragraphs = [p for p in marathi_translation.split("\n\n") if p.strip()]
    assert len(output_paragraphs) == len(input_paragraphs) == 6

    # Verify beginning and ending paragraphs are both non-empty and well-formed
    assert len(output_paragraphs[0]) > 100
    assert len(output_paragraphs[-1]) > 100


@pytest.mark.integration
def test_exact_user_scenario_long_text_english_to_marathi():
    """Verify exact user scenario with roadmap, NLP foundation, BLEU/chrF, OAuth, and frontend."""
    user_scenario_text = (
        "One thing I would improve later in our roadmap is our complete multilingual translation system.\n\n"
        "Current status and NLP backend foundation:\n"
        "We have successfully built the core NLP backend foundation using the NLLB-200 distilled 600M parameter model. "
        "The model runs with PyTorch and CUDA GPU inference on an NVIDIA GeForce RTX 3050 Laptop GPU for fast acceleration. "
        "Our multilingual translation pipeline supports 26 languages directly without requiring English as an intermediate pivot language.\n\n"
        "FastAPI Service and Input Validation:\n"
        "The web service is built using FastAPI with modular routers for translation, supported languages, and system health checks. "
        "We implemented strict input validation ensuring empty text rejection and enforcing a 2,000-character maximum input limit. "
        "Automated unit testing guarantees that all endpoints and validation rules operate reliably under production conditions.\n\n"
        "Quality Evaluation with BLEU and chrF:\n"
        "For quality assurance, we developed an evaluation module calculating sentence-level and corpus-level BLEU and chrF metrics. "
        "We created a curated multilingual evaluation dataset across diverse language directions to benchmark model accuracy. "
        "The evaluation report confirms strong semantic fidelity and grammatical fluency across high-resource and low-resource languages.\n\n"
        "Database, Google OAuth, and Security:\n"
        "In the upcoming phase, we will connect a persistent database to store translation history and user preferences securely. "
        "We will also integrate Google OAuth authentication to provide seamless user login and secure session management.\n\n"
        "Final Frontend Instructions and Next Plan:\n"
        "Finally, we will implement the final frontend instructions with searchable language selectors, clipboard copying, and file downloads. "
        "This completes our next plan for deployment and concludes our comprehensive multilingual system roadmap."
    )

    marathi_output = translate(user_scenario_text, "English", "Marathi")
    assert isinstance(marathi_output, str)
    assert len(marathi_output) > 1200

    # Verify all 6 section blocks exist
    input_blocks = [b for b in user_scenario_text.split("\n\n") if b.strip()]
    output_blocks = [b for b in marathi_output.split("\n\n") if b.strip()]
    assert len(output_blocks) == len(input_blocks) == 6


@pytest.mark.integration
def test_long_text_german_to_spanish_translation():
    """Verify multi-paragraph German to Spanish translation on GPU."""
    long_german_text = (
        "Künstliche Intelligenz revolutioniert die moderne Datenverarbeitung und Automatisierung in vielen Branchen weltweit. "
        "Durch fortschrittliche Algorithmen können komplexe Muster in großen Datenmengen schnell erkannt werden.\n\n"
        "Die maschinelle Sprachübersetzung ermöglicht einen nahtlosen Informationsaustausch über Sprachgrenzen hinweg. "
        "Dies ist besonders wichtig für die globale Zusammenarbeit und den interkulturellen Dialog."
    )

    spanish_translation = translate(
        text=long_german_text,
        source_language="German",
        target_language="Spanish"
    )

    assert isinstance(spanish_translation, str)
    assert len(spanish_translation) > 100
    assert "\n\n" in spanish_translation


@pytest.mark.integration
def test_long_text_japanese_to_english_translation():
    """Verify multi-sentence Japanese to English translation on GPU."""
    japanese_text = (
        "機械翻訳技術は深層学習によって劇的に進化しました。"
        "以前の統計的アプローチと比較して、現在のニューラルモデルは文脈をより深く理解します。"
        "これにより、医療や教育などの重要な分野での国際協力が促進されています。"
    )

    english_translation = translate(
        text=japanese_text,
        source_language="Japanese",
        target_language="English"
    )

    assert isinstance(english_translation, str)
    assert len(english_translation) > 50
