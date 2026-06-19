import json
from unittest.mock import patch, Mock
from slm_pdf.vlm_client import VlmClient


def test_process_page_returns_json():
    fake_response = {
        "pages": [
            {
                "page_number": 1,
                "sections": [{"heading": "Title", "content": "Hello"}],
                "tables": [],
                "metadata": {},
            }
        ]
    }
    mock_post = Mock()
    mock_post.json.return_value = {
        "message": {"content": json.dumps(fake_response)}
    }
    mock_post.raise_for_status = Mock()

    client = VlmClient()
    with patch("httpx.Client.post", return_value=mock_post):
        result = client.process_page(b"fake_png_bytes", 1)

    assert result["page_number"] == 1
    assert result["sections"][0]["content"] == "Hello"


def test_process_page_fallback_on_bad_json():
    mock_post = Mock()
    mock_post.json.return_value = {
        "message": {"content": "Here is some raw text without JSON"}
    }
    mock_post.raise_for_status = Mock()

    client = VlmClient()
    with patch("httpx.Client.post", return_value=mock_post):
        result = client.process_page(b"fake_png_bytes", 1)

    assert "error" in result
    assert result["raw_text"] == "Here is some raw text without JSON"


def test_process_page_http_error():
    mock_post = Mock()
    mock_post.raise_for_status.side_effect = Exception("Connection refused")

    client = VlmClient()
    with patch("httpx.Client.post", return_value=mock_post):
        result = client.process_page(b"fake_png_bytes", 1)

    assert result["error"] is not None
    assert "Connection refused" in str(result["error"])
