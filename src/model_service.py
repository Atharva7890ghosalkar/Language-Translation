import torch

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


MODEL_NAME = "facebook/nllb-200-distilled-600M"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Loading NLLB-200 on: {DEVICE}")

if DEVICE == "cuda":
    print(f"GPU: {torch.cuda.get_device_name(0)}")


tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME,
    dtype=torch.float16 if DEVICE == "cuda" else torch.float32
).to(DEVICE)

print("NLLB-200 loaded successfully.")