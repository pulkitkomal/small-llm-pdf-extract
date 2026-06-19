import time
from pathlib import Path

from slm_pdf.renderer import render_pdf
from slm_pdf.vlm_client import VlmClient
from slm_pdf.parser import parse_page, assemble_document
from slm_pdf.models import DocumentOutput


class Pipeline:
    def __init__(
        self,
        model: str = "qwen2.5-vl:3b",
        endpoint: str = "http://localhost:11434",
        timeout: int = 120,
        dpi: int = 300,
    ):
        self.vlm_client = VlmClient(
            model=model, endpoint=endpoint, timeout=timeout
        )
        self.dpi = dpi

    def run(self, path: str) -> DocumentOutput:
        start = time.time()
        filename = Path(path).name

        rendered_pages = render_pdf(path, dpi=self.dpi)
        if not rendered_pages:
            elapsed = time.time() - start
            return assemble_document([], filename, elapsed)

        page_contents = []
        for page_num, png_bytes, is_blank in rendered_pages:
            if is_blank:
                continue
            result = self.vlm_client.process_page(png_bytes, page_num)
            page_content = parse_page(result, page_num)
            page_contents.append(page_content)

        elapsed = time.time() - start
        return assemble_document(page_contents, filename, elapsed)
