# SLM-PDF

Small Language Model PDF Parser — extracts structured JSON from PDFs on a Raspberry Pi 5 using Qwen2.5-VL-3B via Ollama.

## Architecture

```
PDF → PyMuPDF render (300 DPI) → Qwen2.5-VL-3B-Q4 → structured JSON
```

Each page is rendered as an image and fed to a vision-language model that sees layout, tables, and text natively — no OCR pipeline needed.

## Requirements

- Python 3.11+
- Raspberry Pi 5 (8GB RAM recommended) or any ARM64/aarch64 Linux machine
- [Ollama](https://ollama.ai) with Qwen2.5-VL:3b model pulled

## Install

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install package
pip install -e .

# Pull the model (requires Ollama)
ollama pull qwen2.5-vl:3b
```

## Usage

```bash
# Process a PDF, output JSON to stdout
slm-pdf invoice.pdf

# Save to file
slm-pdf invoice.pdf -o output.json

# Customize model/endpoint
slm-pdf invoice.pdf --model qwen2.5-vl:7b --endpoint http://192.168.1.5:11434
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--output`, `-o` | stdout | Output JSON file path |
| `--model` | `qwen2.5-vl:3b` | Ollama model name |
| `--endpoint` | `http://localhost:11434` | Ollama API URL |
| `--timeout` | `120` | Seconds per page before timeout |
| `--dpi` | `300` | PDF render resolution |

## Output Format

```json
{
  "filename": "invoice.pdf",
  "pages": [
    {
      "page_number": 1,
      "sections": [
        {"heading": "Invoice", "content": "..."}
      ],
      "tables": [
        {"headers": ["Item", "Price"], "rows": [["Widget", "$10"]]}
      ],
      "metadata": {"total": "$100.50", "date": "2024-01-15"}
    }
  ],
  "processing_time_seconds": 45.2
}
```

## Test

```bash
pytest tests/ -v
```

## Hardware Budget

| Resource | Estimate |
|----------|----------|
| RAM | ~3-4 GB |
| Disk | ~2-3 GB (model + code) |
| Per-page latency | ~30-60s (Pi 5, CPU) |
| Daily throughput | ~50-200 pages |
