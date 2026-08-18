# Multilingual Language Translation NLP

A production-grade, local neural machine translation system powered by Meta's **`facebook/nllb-200-distilled-600M`** model. Built with **PyTorch**, **CUDA GPU acceleration**, a **FastAPI** backend, and an interactive **HTML/CSS/JavaScript** web interface.

The application currently exposes **26 supported languages** with real-time translation, short and multi-sentence robustness, intelligent long-text chunking up to 2,000 characters, and automated BLEU & chrF metric evaluation.

---

## 1. Features

- **26 Exposing Supported Languages**: Real-time translation between 26 major global and regional languages (English, Hindi, French, German, Spanish, Italian, Japanese, Chinese, Marathi, and more).
- **NLLB-200 Engine**: High-quality sequence-to-sequence translation using Meta's `facebook/nllb-200-distilled-600M`.
- **CUDA GPU Acceleration**: Optimized for local NVIDIA CUDA execution with dynamic token budgeting.
- **FastAPI Backend**: High-performance asynchronous REST API with structured Pydantic validation.
- **Short & Multi-Sentence Robustness**: Sentence-aware splitting ensuring complete multi-sentence translation regardless of punctuation (`.`, `!`, `?`, `।`, `|`, `。`, `！`, `？`) or missing trailing spaces.
- **Long-Text Chunking Pipeline**: Paragraph and sentence-aware segmentation supporting inputs up to 2,000 characters without silent data truncation.
- **Oversized & CJK Fallback**: Token-slice subdivision and fallback retry logic for run-on sentences and space-less scripts (e.g., Japanese, Chinese).
- **Interactive Web Interface**: Clean, responsive frontend featuring custom searchable language dropdowns, instant language swap, copy to clipboard, and UTF-8 `.txt` translation download.
- **3D Beam Grid Background**: Animated perspective grid, travelling light beam scan, and outer edge node network.
- **Automated Metric Evaluation**: BLEU and chrF scoring pipeline with a curated multilingual benchmark dataset.
- **Comprehensive Test Suite**: 36 automated unit and integration tests verifying API endpoints, chunking, and translation robustness.

---

## 2. Architecture

### Application Workflow
```
User (Browser)
  │
  ▼
HTML / CSS / JavaScript Frontend
  │ (REST API / HTTP)
  ▼
FastAPI Server (src/api/main.py)
  │
  ▼
Translation Engine (src/translator.py)
  ├─► Single-Sentence Fast Path (<=120 tokens, 1 sentence)
  └─► Sentence/Paragraph-Aware Chunking (Multi-sentence / Long text)
  │
  ▼
Model Service (src/model_service.py)
  │ (HuggingFace Transformers)
  ▼
NLLB-200 Model (facebook/nllb-200-distilled-600M)
  │
  ▼
PyTorch + NVIDIA CUDA GPU
  │
  ▼
Translated Output Text
```

### Evaluation Workflow
```
Evaluation Dataset (data/evaluation/evaluation_set.json)
  │
  ▼
Evaluation Script (scripts/evaluate_model.py)
  │
  ▼
Translation Engine (NLLB-200)
  │
  ▼
SacreBLEU & chrF Metrics (src/evaluation/metrics.py)
  │
  ▼
Evaluation Report (data/evaluation/evaluation_report.json)
```

---

## 3. Tech Stack

- **Language**: Python 3.12
- **Deep Learning Framework**: PyTorch 2.11.0 (CUDA 12.8 build)
- **NLP / Model Library**: Hugging Face `transformers` 4.38+, `sentencepiece`
- **Model**: `facebook/nllb-200-distilled-600M`
- **Backend Web Framework**: FastAPI 0.110+, Uvicorn, Pydantic v2
- **Evaluation & Metrics**: SacreBLEU 2.4+
- **Testing & HTTP Client**: Pytest 8.0+, HTTPX
- **Frontend**: HTML5, CSS3 (CSS Variables, Flexbox/Grid, Backdrop Filter), Vanilla JavaScript (ES6+)

---

## 4. Project Structure

```
Language Translation NLP/
├── data/
│   └── evaluation/
│       ├── evaluation_set.json      # Benchmark evaluation sentence pairs
│       └── evaluation_report.json   # Output BLEU / chrF metric results
├── scripts/
│   └── evaluate_model.py            # CLI script to evaluate NLLB-200 on benchmark dataset
├── src/
│   ├── api/
│   │   ├── main.py                  # FastAPI application & endpoints
│   │   ├── routes/                  # API route handlers
│   │   └── schemas.py               # Request/Response Pydantic schemas
│   ├── evaluation/
│   │   └── metrics.py               # BLEU and chrF score computation engine
│   ├── static/
│   │   ├── app.js                   # Client-side UI logic & searchable dropdowns
│   │   ├── index.html               # Main frontend markup & background scene
│   │   └── styles.css               # Design system & Beam Grid animations
│   ├── language_codes.py            # 26 supported language mappings (FLORES-200 codes)
│   ├── language_utils.py            # Code lookup & validation utilities
│   ├── model_service.py             # Model initialization & GPU device loading
│   └── translator.py                # Translation pipeline, chunking, & sentence splitter
├── tests/
│   ├── test_api.py                  # FastAPI endpoint unit tests
│   ├── test_evaluation.py           # BLEU / chrF metric calculation tests
│   ├── test_language_utils.py       # Language code & utility tests
│   ├── test_long_text.py            # 2,000-character long text chunking tests
│   ├── test_multi_sentence.py       # Multi-sentence & punctuation robustness tests
│   └── test_translation_integration.py # End-to-end translation pipeline tests
├── .gitignore                       # Git ignore configuration
├── requirements.txt                 # Python package dependencies
└── README.md                        # Project documentation
```

---

## 5. Installation & Setup

### Prerequisites
- **Python**: Recommended version `3.12.x`
- **OS**: Windows / Linux / macOS (NVIDIA GPU recommended for optimal performance)

### Step 1: Clone the Repository
```powershell
git clone https://github.com/Atharva7890ghosalkar/Language-Translation.git
cd Language-Translation
```

### Step 2: Create a Virtual Environment
```powershell
python -3.12 -m venv .venv
```

### Step 3: Activate the Virtual Environment
- **Windows (PowerShell)**:
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- **Linux / macOS**:
  ```bash
  source .venv/bin/activate
  ```

### Step 4: Upgrade Pip & Install Dependencies
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

> **Note**: `requirements.txt` specifies `torch>=2.2.0` and required NLP packages. For CUDA 12.8 GPU support, ensure PyTorch is installed with CUDA enabled (e.g., `pip install torch --index-url https://download.pytorch.org/whl/cu128`).

---

## 6. GPU Requirement & Performance

- **Tested Environment**: NVIDIA GeForce RTX 3050 Laptop GPU (4 GB VRAM) running PyTorch `2.11.0+cu128` on Windows 11.
- **CUDA Acceleration**: Model weights (`facebook/nllb-200-distilled-600M`) are loaded into GPU memory in `float16` precision for fast inference.
- **CPU Fallback**: If an NVIDIA GPU is not detected, `model_service.py` automatically falls back to CPU execution (`float32`). Translation will be functional, but inference latency per chunk will be higher.

---

## 7. Running the Application

Start the FastAPI server using Uvicorn:

```powershell
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

Once started:
- **Web Application UI**: Open [http{://}127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.
- **Interactive Swagger API Docs**: Open [http{://}127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

## 8. API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the main frontend web application (`index.html`) |
| `GET` | `/health` | Returns health status, loaded model name, and GPU availability |
| `GET` | `/languages` | Returns the list of 26 supported languages |
| `POST` | `/translate` | Translates input text (up to 2,000 characters) |

### Request Example (`POST /translate`)
```json
{
  "text": "Hello, how are you? What are you doing?",
  "source_language": "English",
  "target_language": "Hindi"
}
```

### Response Example
```json
{
  "translated_text": "हैलो, आप कैसे हैं? तुम क्या कर रहे हो?",
  "source_language": "English",
  "target_language": "Hindi"
}
```

---

## 9. Long-Text & Multi-Sentence Pipeline

The application enforces an application-level input limit of **2,000 characters** per request to preserve system stability.

To ensure high translation quality across short and long texts:
1. **Single-Sentence Fast Path**: Inputs containing a single sentence ($\le 120$ tokens) are processed directly in a single pass.
2. **Multi-Sentence Splitting**: Multilingual punctuation boundaries (`.`, `!`, `?`, `।`, `|`, `。`, `！`, `？`) are split into logical sentences, avoiding truncation even when trailing spaces are missing.
3. **Paragraph Preservation**: Newline characters (`\n`) are preserved to maintain structural formatting.
4. **Token Budgeting & Fallback Retry**: Oversized sentences or space-less CJK scripts are subdivided into bounded token slices with subdivision retries to guarantee zero data loss.

---

## 10. Model Evaluation Benchmark

The repository includes a curated evaluation benchmark dataset located at `data/evaluation/evaluation_set.json`.

- **Metrics Used**:
  - **BLEU Score** (via SacreBLEU): Measures n-gram overlap against reference translations.
  - **chrF Score** (via SacreBLEU): Character n-gram F-score, effective for morphologically rich scripts (e.g., Hindi, Japanese).
- **Test Directions**: 24 sentence pairs covering English, Hindi, French, German, Spanish, and Japanese directions.

### Run Evaluation Script
```powershell
python scripts/evaluate_model.py
```

The output report will be updated at `data/evaluation/evaluation_report.json`.

---

## 11. Testing

Run the full automated test suite using `pytest`:

```powershell
python -m pytest
```

### Test Coverage (36 Automated Tests)
- `tests/test_api.py`: Endpoint response verification, health check, invalid language errors, and payload validation.
- `tests/test_multi_sentence.py`: Punctuation boundary detection (`?`, `!`, `.`, `?What`) and multi-sentence translation accuracy.
- `tests/test_long_text.py`: Paragraph chunking, token slicing, and 2,000-character input boundary tests.
- `tests/test_language_utils.py`: Language code lookup, FLORES-200 mapping, and normalization tests.
- `tests/test_evaluation.py`: SacreBLEU and chrF metric computation tests.
- `tests/test_translation_integration.py`: End-to-end model inference pipeline integration tests.

---

## 12. Frontend Overview

The web UI is built using responsive vanilla web technologies:
- **Searchable Custom Dropdowns**: Dynamic search filtering across all 26 supported languages.
- **Language Swap Button**: Quick keybinding/click to swap source and target languages.
- **Utility Actions**: One-click **Copy to Clipboard** and **Download Text** (`.txt`).
- **Responsive Workspace**: Flexible side-by-side or stacked editor panes with character counters.
- **Visual Depth & Background**: Dark theme with translucent surface cards, subtle ambient glows, and a 3D Beam Grid canvas.

---

## 13. Current Scope & Future Work

### Current Scope
- 26 supported languages exposed through API and UI.
- Local NLLB-200 model execution on GPU/CPU.
- Multi-sentence and long-text chunking up to 2,000 characters.

### Planned Future Work
- [ ] User authentication & account management.
- [ ] Database-backed translation history and saved favorites.
- [ ] Persistent user preferences (default language pairs, UI themes).
- [ ] Expansion to additional FLORES-200 language pairs.
- [ ] Automated source language detection.
