from slm_pdf.parser import parse_page, assemble_document
from slm_pdf.models import PageContent, DocumentOutput


def test_parse_page_valid():
    data = {
        "page_number": 1,
        "sections": [{"heading": "Title", "content": "Hello"}],
        "tables": [{"headers": ["A"], "rows": [["1"]]}],
        "metadata": {"date": "2024-01-01"},
    }
    page = parse_page(data, 1)
    assert page.page_number == 1
    assert len(page.sections) == 1
    assert page.sections[0].heading == "Title"
    assert len(page.tables) == 1
    assert page.tables[0].headers == ["A"]
    assert page.metadata == {"date": "2024-01-01"}
    assert page.error is None


def test_parse_page_with_error():
    data = {"error": "Ollama timeout", "raw_text": "some text"}
    page = parse_page(data, 1)
    assert page.error == "Ollama timeout"
    assert page.raw_text == "some text"


def test_parse_page_empty_data():
    page = parse_page({}, 1)
    assert page.page_number == 1
    assert page.sections == []
    assert page.tables == []
    assert page.metadata == {}


def test_assemble_document():
    pages = [
        PageContent(page_number=1, sections=[], metadata={"key": "val"})
    ]
    doc = assemble_document(pages, "test.pdf", 10.5)
    assert doc.filename == "test.pdf"
    assert len(doc.pages) == 1
    assert doc.processing_time_seconds == 10.5


def test_assemble_document_empty():
    doc = assemble_document([], "empty.pdf", 0.0)
    assert doc.filename == "empty.pdf"
    assert doc.pages == []
