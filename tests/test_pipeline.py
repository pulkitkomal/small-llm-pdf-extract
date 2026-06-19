import tempfile
from pathlib import Path
from unittest.mock import patch, Mock

import fitz
from slm_pdf.pipeline import Pipeline


def _make_test_pdf(text: str = "Test content") -> Path:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), text)
    pdf_bytes = doc.write()
    doc.close()
    path = Path(tempfile.mktemp(suffix=".pdf"))
    path.write_bytes(pdf_bytes)
    return path


def test_pipeline_returns_document_output():
    path = _make_test_pdf("Hello world")
    pipeline = Pipeline()

    with patch.object(
        pipeline.vlm_client, "process_page", return_value={
            "page_number": 1,
            "sections": [{"heading": "", "content": "Hello world"}],
            "tables": [],
            "metadata": {},
        }
    ):
        result = pipeline.run(str(path))

    assert result.filename == path.name
    assert len(result.pages) == 1
    assert result.pages[0].sections[0].content == "Hello world"
    assert result.processing_time_seconds > 0


def test_pipeline_skips_blank_pages():
    doc = fitz.open()
    doc.new_page()
    page2 = doc.new_page()
    page2.insert_text((50, 50), "Content")
    pdf_bytes = doc.write()
    doc.close()
    path = Path(tempfile.mktemp(suffix=".pdf"))
    path.write_bytes(pdf_bytes)

    pipeline = Pipeline()
    with patch.object(
        pipeline.vlm_client, "process_page", return_value={
            "page_number": 2,
            "sections": [{"heading": "", "content": "Content"}],
            "tables": [],
            "metadata": {},
        }
    ):
        result = pipeline.run(str(path))

    assert len(result.pages) == 1
    assert result.pages[0].page_number == 2


def test_pipeline_corrupt_pdf():
    path = Path(tempfile.mktemp(suffix=".pdf"))
    path.write_bytes(b"corrupt data")

    pipeline = Pipeline()
    result = pipeline.run(str(path))
    assert result.filename == path.name
    assert result.pages == []


def test_pipeline_handles_vlm_error():
    path = _make_test_pdf("Some text")
    pipeline = Pipeline()

    with patch.object(
        pipeline.vlm_client,
        "process_page",
        return_value={
            "page_number": 1,
            "error": "Ollama not running",
            "raw_text": "",
            "sections": [],
            "tables": [],
            "metadata": {},
        },
    ):
        result = pipeline.run(str(path))

    assert len(result.pages) == 1
    assert result.pages[0].error == "Ollama not running"
