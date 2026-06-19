import logging
import time
from pathlib import Path

from slm_pdf.renderer import render_pdf
from slm_pdf.vlm_client import VlmClient
from slm_pdf.parser import parse_page, assemble_document
from slm_pdf.models import DocumentOutput

logger = logging.getLogger(__name__)


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
        logger.info(
            "Pipeline: model=%s endpoint=%s timeout=%ds dpi=%d",
            model, endpoint, timeout, dpi,
        )

    def run(self, path: str) -> DocumentOutput:
        start = time.time()
        filename = Path(path).name
        logger.info("Processing PDF: %s", path)

        rendered_pages = render_pdf(path, dpi=self.dpi)
        if not rendered_pages:
            elapsed = time.time() - start
            logger.warning("No pages rendered from %s", path)
            return assemble_document([], filename, elapsed)

        non_blank = sum(1 for _, _, b in rendered_pages if not b)
        blank = sum(1 for _, _, b in rendered_pages if b)
        logger.info("Pages: %d non-blank, %d blank", non_blank, blank)

        page_contents = []
        for page_num, png_bytes, is_blank in rendered_pages:
            if is_blank:
                logger.debug("Skipping blank page %d", page_num)
                continue
            t0 = time.time()
            result = self.vlm_client.process_page(png_bytes, page_num)
            page_content = parse_page(result, page_num)
            elapsed_page = time.time() - t0
            logger.info("Page %d done in %.1fs", page_num, elapsed_page)
            page_contents.append(page_content)

        elapsed = time.time() - start
        doc = assemble_document(page_contents, filename, elapsed)
        logger.info("Total: %.1fs for %s", elapsed, filename)
        return doc
