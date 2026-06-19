import base64
import json
import logging
import re
import time
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a PDF document analyzer. Extract all content from the page image and return it as JSON.

Return this exact JSON structure:
{
  "pages": [
    {
      "page_number": <int>,
      "sections": [
        {"heading": "<section heading or empty string>", "content": "<section text>"}
      ],
      "tables": [
        {"headers": ["col1", "col2", ...], "rows": [["val1", "val2", ...], ...]}
      ],
      "metadata": {"key1": "value1", ...}
    }
  ]
}

Rules:
- Extract ALL text visible on the page
- Identify tables and output them with headers and rows
- Put any key-value pairs (dates, totals, names, etc.) in metadata
- If a page has no structured content, put all text in a single section with empty heading
- Return ONLY valid JSON, no other text"""


class VlmClient:
    def __init__(
        self,
        model: str = "qwen2.5-vl:3b",
        endpoint: str = "http://localhost:11434",
        timeout: int = 120,
    ):
        self.model = model
        self.endpoint = endpoint.rstrip("/")
        self.timeout = timeout
        logger.info("VlmClient: model=%s endpoint=%s timeout=%ds", model, endpoint, timeout)

    def process_page(
        self, png_bytes: bytes, page_number: int, retry: bool = True
    ) -> dict:
        b64_image = base64.b64encode(png_bytes).decode("utf-8")
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": "",
                    "images": [b64_image],
                },
            ],
            "stream": False,
            "options": {"temperature": 0.1},
        }

        img_size = len(png_bytes) >> 10
        logger.info("Page %d: sending %dKB image to %s", page_number, img_size, self.model)

        try:
            t0 = time.time()
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(
                    f"{self.endpoint}/api/chat", json=payload
                )
                resp.raise_for_status()
                data = resp.json()
                content = data.get("message", {}).get("content", "")
            elapsed = time.time() - t0
            logger.info("Page %d: Ollama responded in %.1fs (%d chars)", page_number, elapsed, len(content))
        except Exception as e:
            logger.error("Page %d: Ollama request failed: %s", page_number, e)
            return {
                "page_number": page_number,
                "error": str(e),
                "raw_text": "",
                "sections": [],
                "tables": [],
                "metadata": {},
            }

        parsed = self._parse_json(content)
        if parsed is not None:
            logger.info("Page %d: JSON parsed successfully", page_number)
            return parsed.get("pages", [{}])[0] if parsed.get("pages") else parsed

        logger.warning("Page %d: failed to parse JSON from model output, retrying...", page_number)
        if retry:
            return self._retry_simple(png_bytes, page_number)

        return self._fallback(content, page_number)

    def _retry_simple(self, png_bytes: bytes, page_number: int) -> dict:
        logger.info("Page %d: retrying with simplified prompt", page_number)
        b64_image = base64.b64encode(png_bytes).decode("utf-8")
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": "Extract all text from this page as JSON with 'text' and 'tables' fields.",
                    "images": [b64_image],
                }
            ],
            "stream": False,
            "options": {"temperature": 0.1},
        }
        try:
            t0 = time.time()
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(
                    f"{self.endpoint}/api/chat", json=payload
                )
                resp.raise_for_status()
                data = resp.json()
                content = data.get("message", {}).get("content", "")
            elapsed = time.time() - t0
            logger.info("Page %d: retry responded in %.1fs", page_number, elapsed)
        except Exception as e:
            logger.error("Page %d: retry also failed: %s", page_number, e)
            return self._fallback("", page_number)

        parsed = self._parse_json(content)
        if parsed is not None:
            logger.info("Page %d: retry JSON parsed successfully", page_number)
            return parsed.get("pages", [{}])[0] if parsed.get("pages") else parsed
        logger.warning("Page %d: retry also produced unparseable output", page_number)
        return self._fallback(content, page_number)

    def _parse_json(self, text: str) -> Optional[dict]:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except json.JSONDecodeError:
                pass
        return None

    def _fallback(self, content: str, page_number: int) -> dict:
        logger.warning("Page %d: storing raw text as fallback", page_number)
        return {
            "page_number": page_number,
            "sections": [],
            "tables": [],
            "metadata": {},
            "raw_text": content,
            "error": "Failed to parse JSON from model output",
        }
