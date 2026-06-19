import io
from pathlib import Path

import fitz
from PIL import Image


def render_pdf(path: str, dpi: int = 300) -> list[tuple[int, bytes, bool]]:
    pages: list[tuple[int, bytes, bool]] = []
    try:
        doc = fitz.open(path)
    except Exception:
        return pages

    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)

    for page_num in range(len(doc)):
        page = doc[page_num]
        try:
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            png_bytes = buf.getvalue()

            is_blank = _is_blank(img)
            pages.append((page_num + 1, png_bytes, is_blank))
        except Exception:
            continue

    doc.close()
    return pages


def _is_blank(img: Image.Image) -> bool:
    gray = img.convert("L")
    extrema = gray.getextrema()
    return extrema == (255, 255)
