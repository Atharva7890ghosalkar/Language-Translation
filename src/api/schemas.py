from pydantic import BaseModel, Field


class TranslationRequest(BaseModel):
    text: str = Field(
        ...,
        description="The text to be translated.",
        min_length=1,
        max_length=2000,
        examples=["Hello, how are you?"]
    )
    source_language: str = Field(
        ...,
        description="Human-readable source language name.",
        examples=["English"]
    )
    target_language: str = Field(
        ...,
        description="Human-readable target language name.",
        examples=["French"]
    )


class TranslationResponse(BaseModel):
    source_language: str
    target_language: str
    source_text: str
    translated_text: str


class LanguagesResponse(BaseModel):
    languages: list[str]


class HealthResponse(BaseModel):
    status: str
    service: str
    device: str
