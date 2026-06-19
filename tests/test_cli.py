import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import fitz
from slm_pdf.cli import main


def _make_test_pdf() -> Path:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "CLI test")
    pdf_bytes = doc.write()
    doc.close()
    path = Path(tempfile.mktemp(suffix=".pdf"))
    path.write_bytes(pdf_bytes)
    return path


def test_cli_help():
    try:
        main(["--help"])
    except SystemExit as e:
        assert e.code == 0


def test_cli_basic_run(capsys):
    path = _make_test_pdf()
    with patch(
        "slm_pdf.pipeline.Pipeline.run"
    ) as mock_run:
        mock_run.return_value.model_dump.return_value = {
            "filename": path.name,
            "pages": [{"page_number": 1, "sections": [], "tables": [], "metadata": {}, "raw_text": "", "error": None}],
            "processing_time_seconds": 1.0,
        }
        main([str(path), "--output", "/tmp/test_output.json"])

    with open("/tmp/test_output.json") as f:
        data = json.load(f)
    assert data["filename"] == path.name


def test_cli_stdout(capsys):
    path = _make_test_pdf()
    with patch(
        "slm_pdf.pipeline.Pipeline.run"
    ) as mock_run:
        mock_run.return_value.model_dump.return_value = {
            "filename": path.name,
            "pages": [],
            "processing_time_seconds": 0.5,
        }
        main([str(path)])

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["filename"] == path.name
