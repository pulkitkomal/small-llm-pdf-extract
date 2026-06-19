# SLM-PDF: Small Language Model PDF Parser

**Date:** 2026-06-19
**Hardware:** Raspberry Pi 5 (ARM CPU, no GPU)

## Goal

Process arbitrary PDFs (scanned, digital, tables, forms, mixed content) on a Raspberry Pi 5 into structured JSON output using a small vision-language model (1B-4B parameters), matching high-end PDF parser quality.

## Architecture

```
PDF file → Page Renderer (PyMuPDF) → Qwen2.5-VL-3B-Q4 → JSON output
```

Single pipeline: render each page as an image, feed to a vision-language model via Ollama, collect structured JSON.

## Components

### 1. PDF Page Renderer
- **Library:** PyMuPDF (fitz)
- **Resolution:** 300 DPI, PNG format
- **Handles:** Scanned docs, digital PDFs, mixed content
- **Blanks:** Detected and skipped
- **Errors:** Corrupt/password-protected PDFs → graceful skip with report

### 2. VLM Inference
- **Runtime:** llama.cpp via Ollama
- **Model:** Qwen2.5-VL-3B-Instruct (4-bit GGUF)
- **Prompt:** System prompt with JSON schema + few-shot examples
- **Concurrency:** One page at a time (RAM constraint)

### 3. Structured Output Parser
- Try JSON.parse → regex extraction → raw text fallback
- Schema validation on output
- Retry once on parse failure with simplified prompt

### 4. Output Format

```json
{
  "filename": "invoice-123.pdf",
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

## Data Flow

```
PDF → render each page → blank? skip
                       → has content? → Ollama inference
                                       → JSON parse
                                       → schema validation
                                       → pass: collect
                                       → fail: retry once
                                             → still fail: store raw + error flag
→ assemble final JSON
```

## Error Handling

| Scenario | Response |
|---|---|
| Corrupt PDF | Report filename, skip |
| JSON parse failure | Retry once, then store raw text with error flag |
| Out of memory | Process single page at a time (default) |
| Timeout | Configurable (default 120s/page), then skip |

## Testing Strategy

- **Renderer:** Unit test with known PDFs, verify dimensions, detect blanks
- **Model prompts:** Test against curated PDFs with expected JSON
- **End-to-end:** 5-10 varied PDFs, manual quality verification
- **Regression:** Store test PDFs + expected outputs in repo

## Hardware Budget

| Resource | Estimate |
|---|---|
| RAM | ~3-4 GB |
| Disk | ~2-3 GB (model + code) |
| Per-page latency | ~30-60s |
| Daily throughput | ~50-200 pages |

## Future Considerations (not in scope)

- GPU acceleration (Pi 5 has no GPU; future Pi with NPU)
- Batching/multi-page context
- Custom fine-tuning for specific document types
