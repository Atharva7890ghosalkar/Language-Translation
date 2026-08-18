import sys
from unittest.mock import MagicMock, patch

# Mock src.model_service before importing app to avoid loading heavy NLLB model during unit/API tests
mock_model_service = MagicMock()
mock_model_service.DEVICE = "cuda"
mock_model_service.model = MagicMock()
mock_model_service.tokenizer = MagicMock()
sys.modules["src.model_service"] = mock_model_service

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)



def test_root_serves_frontend():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "LANGUAGE TRANSLATION" in response.text


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "Language Translation API"
    assert "device" in data


def test_get_languages_endpoint():
    response = client.get("/languages")
    assert response.status_code == 200
    data = response.json()
    assert "languages" in data
    assert isinstance(data["languages"], list)
    assert "English" in data["languages"]
    assert "French" in data["languages"]


def test_translate_same_language_shortcut():
    payload = {
        "text": "Bonjour tout le monde",
        "source_language": "French",
        "target_language": "French"
    }
    response = client.post("/translate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["translated_text"] == "Bonjour tout le monde"
    assert data["source_language"] == "French"
    assert data["target_language"] == "French"


def test_translate_empty_text():
    payload = {
        "text": "   ",
        "source_language": "English",
        "target_language": "French"
    }
    response = client.post("/translate", json=payload)
    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"].lower()


def test_translate_excessive_length():
    payload = {
        "text": "a" * 2005,
        "source_language": "English",
        "target_language": "French"
    }
    response = client.post("/translate", json=payload)
    assert response.status_code in (400, 422)
    detail_str = str(response.json()["detail"]).lower()
    assert "2000" in detail_str or "exceeds" in detail_str or "at most" in detail_str




def test_translate_unsupported_source_language():
    payload = {
        "text": "Hello",
        "source_language": "Klingon",
        "target_language": "French"
    }
    response = client.post("/translate", json=payload)
    assert response.status_code == 400
    assert "Unsupported source language" in response.json()["detail"]


def test_translate_unsupported_target_language():
    payload = {
        "text": "Hello",
        "source_language": "English",
        "target_language": "Elvish"
    }
    response = client.post("/translate", json=payload)
    assert response.status_code == 400
    assert "Unsupported target language" in response.json()["detail"]


@patch("src.api.routes.translation.translate")
def test_translate_valid_request(mock_translate):
    mock_translate.return_value = "Bonjour le monde"

    payload = {
        "text": "Hello world",
        "source_language": "English",
        "target_language": "French"
    }
    response = client.post("/translate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["source_language"] == "English"
    assert data["target_language"] == "French"
    assert data["source_text"] == "Hello world"
    assert data["translated_text"] == "Bonjour le monde"
    mock_translate.assert_called_once_with(
        text="Hello world",
        source_language="English",
        target_language="French"
    )
