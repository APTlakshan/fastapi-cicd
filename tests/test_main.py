from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app.main import app, ml_models

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "SmolLM" in data["model"]

def test_generate_text_mocked():
    # Test එක run වෙද්දී model එක memory එකේ නැත්නම් dummy objects inject කිරීම
    mock_tokenizer = MagicMock()
    mock_model = MagicMock()

    # Tokenizer behavior simulate කිරීම
    mock_tokenizer.apply_chat_template.return_value = "<user>Hi</user>"
    mock_tokenizer.return_value = {"input_ids": MagicMock(shape=[1, 5])}
    mock_tokenizer.eos_token_id = 0
    mock_tokenizer.decode.return_value = "Hello! I am SmolLM."

    # Model behavior simulate කිරීම
    mock_model.generate.return_value = [[0, 1, 2, 3, 4, 5, 6]]

    # Global dictionary එකට mock objects දැමීම
    ml_models["tokenizer"] = mock_tokenizer
    ml_models["model"] = mock_model

    # Request එක යැවීම
    payload = {
        "prompt": "Say hello",
        "max_tokens": 20,
        "temperature": 0.5
    }
    response = client.post("/generate", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["prompt"] == "Say hello"
    assert data["response"] == "Hello! I am SmolLM."

def test_invalid_payload():
    # වැරදි data type එකක් යැවූ විට 422 Unprocessable Entity error එක එනවාදැයි බැලීම
    payload = {
        "max_tokens": "invalid_number"
    }
    response = client.post("/generate", json=payload)
    assert response.status_code == 422