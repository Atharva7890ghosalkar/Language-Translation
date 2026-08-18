import pytest
from src.language_utils import (
    get_supported_languages,
    is_supported_language,
    get_language_code,
)


def test_get_supported_languages():
    languages = get_supported_languages()
    assert isinstance(languages, list)
    assert len(languages) > 0
    assert "English" in languages
    assert "French" in languages
    assert "Hindi" in languages
    assert "Japanese" in languages


def test_is_supported_language():
    assert is_supported_language("English") is True
    assert is_supported_language("French") is True
    assert is_supported_language("Spanish") is True
    assert is_supported_language("Klingon") is False
    assert is_supported_language("") is False


def test_get_language_code_valid():
    assert get_language_code("English") == "eng_Latn"
    assert get_language_code("French") == "fra_Latn"
    assert get_language_code("Hindi") == "hin_Deva"
    assert get_language_code("Japanese") == "jpn_Jpan"


def test_get_language_code_invalid():
    with pytest.raises(ValueError, match="Unsupported language"):
        get_language_code("InvalidLanguageName")
