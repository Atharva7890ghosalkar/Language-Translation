from fastapi import APIRouter, HTTPException, status

from src.language_utils import get_supported_languages, is_supported_language
from src.translator import translate
from src.api.schemas import (
    TranslationRequest,
    TranslationResponse,
    LanguagesResponse,
)

router = APIRouter()

MAX_TEXT_LENGTH = 2000


@router.get("/languages", response_model=LanguagesResponse)
def get_languages() -> LanguagesResponse:
    """Return all supported language names."""
    languages = get_supported_languages()
    return LanguagesResponse(languages=languages)


@router.post("/translate", response_model=TranslationResponse)
def translate_text(request: TranslationRequest) -> TranslationResponse:
    """Translate input text from source language to target language."""
    cleaned_text = request.text.strip()
    if not cleaned_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text to translate cannot be empty."
        )

    if len(request.text) > MAX_TEXT_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Text length exceeds maximum limit of {MAX_TEXT_LENGTH} characters."
        )

    if not is_supported_language(request.source_language):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported source language: '{request.source_language}'"
        )

    if not is_supported_language(request.target_language):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported target language: '{request.target_language}'"
        )

    # Shortcut: Same source and target language returns original text without model invocation
    if request.source_language == request.target_language:
        return TranslationResponse(
            source_language=request.source_language,
            target_language=request.target_language,
            source_text=request.text,
            translated_text=request.text
        )

    try:
        translated_result = translate(
            text=request.text,
            source_language=request.source_language,
            target_language=request.target_language
        )

        return TranslationResponse(
            source_language=request.source_language,
            target_language=request.target_language,
            source_text=request.text,
            translated_text=translated_result
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(exc)}"
        )
