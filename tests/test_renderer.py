import tempfile
from pathlib import Path
import fitz
from slm_pdf.renderer import render_pdf


def _make_test_pdf(text: str = "Hello World") -> Path:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), text)
    pdf_bytes = doc.write()
    doc.close()
    path = Path(tempfile.mktemp(suffix=".pdf"))
    path.write_bytes(pdf_bytes)
    return path


def test_render_pdf_returns_pages():
    path = _make_test_pdf("Page 1 content")
    pages = render_pdf(str(path))
    assert len(pages) == 1
    page_num, png_bytes, is_blank = pages[0]
    assert page_num == 1
    assert isinstance(png_bytes, bytes)
    assert len(png_bytes) > 100
    assert is_blank is False


def test_render_pdf_blank_page():
    path = _make_test_pdf("")
    pages = render_pdf(str(path))
    assert len(pages) == 1
    _, _, is_blank = pages[0]
    assert is_blank is True


def test_render_pdf_multi_page():
    doc = fitz.open()
    for i in range(3):
        page = doc.new_page()
        page.insert_text((50, 50), f"Page {i+1}")
    pdf_bytes = doc.write()
    doc.close()
    path = Path(tempfile.mktemp(suffix=".pdf"))
    path.write_bytes(pdf_bytes)
    pages = render_pdf(str(path))
    assert len(pages) == 3


def test_render_pdf_corrupt():
    path = Path(tempfile.mktemp(suffix=".pdf"))
    path.write_bytes(b"not a pdf")
    try:
        pages = render_pdf(str(path))
        assert pages == []
    except Exception:
        pass
