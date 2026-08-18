try:
    from src.language_codes import LANGUAGE_CODES
except ImportError:
    from language_codes import LANGUAGE_CODES



def get_supported_languages() -> list[str]:
    """Return all supported language names."""
    return list(LANGUAGE_CODES.keys())


def is_supported_language(language: str) -> bool:
    """Check whether a language is supported."""
    return language in LANGUAGE_CODES


def get_language_code(language: str) -> str:
    """Return the NLLB language code for a language."""
    if not is_supported_language(language):
        raise ValueError(f"Unsupported language: {language}")

    return LANGUAGE_CODES[language]


if __name__ == "__main__":

    print("Supported languages:")
    print(get_supported_languages())

    print()
    print("French supported:", is_supported_language("French"))
    print("French NLLB code:", get_language_code("French"))