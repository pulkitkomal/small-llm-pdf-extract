import io
import logging
from pathlib import Path

import fitz
from PIL import Image

logger = logging.getLogger(__name__)


def render_pdf(path: str, dpi: int = 300) -> list[tuple[int, bytes, bool]]:
    pages: list[tuple[int, bytes, bool]] = []
    try:
        doc = fitz.open(path)
    except Exception as e:
        logger.warning("Failed to open PDF %s: %s", path, e)
        return pages

    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)
    total = len(doc)
    logger.info("Rendering %s — %d pages at %d DPI", path, total, dpi)

    for page_num in range(total):
        page = doc[page_num]
        try:
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            png_bytes = buf.getvalue()

            is_blank = _is_blank(img)
            label = "blank" if is_blank else f"{len(png_bytes) >> 10}KB"
            logger.debug("Page %d: %s", page_num + 1, label)
            pages.append((page_num + 1, png_bytes, is_blank))
        except Exception as e:
            logger.warning("Failed to render page %d: %s", page_num + 1, e)
            continue

    doc.close()
    logger.info("Rendered %d/%d pages", len(pages), total)
    return pages


def _is_blank(img: Image.Image) -> bool:
    gray = img.convert("L")
    extrema = gray.getextrema()
    return extrema == (255, 255)
