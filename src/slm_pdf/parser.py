import logging

from slm_pdf.models import PageContent, DocumentOutput, SectionContent, TableContent

logger = logging.getLogger(__name__)


def parse_page(data: dict, page_number: int) -> PageContent:
    sections_raw = data.get("sections", [])
    sections = [
        SectionContent(heading=s.get("heading", ""), content=s.get("content", ""))
        for s in sections_raw
    ]
    tables_raw = data.get("tables", [])
    tables = [
        TableContent(headers=t.get("headers", []), rows=t.get("rows", []))
        for t in tables_raw
    ]

    page = PageContent(
        page_number=page_number,
        sections=sections,
        tables=tables,
        metadata=data.get("metadata", {}),
        raw_text=data.get("raw_text", ""),
        error=data.get("error"),
    )

    if page.error:
        logger.warning("Page %d: parse error: %s", page_number, page.error)
    else:
        logger.debug(
            "Page %d: %d sections, %d tables, %d metadata keys",
            page_number,
            len(sections),
            len(tables),
            len(page.metadata),
        )
    return page


def assemble_document(
    pages: list[PageContent], filename: str, elapsed: float
) -> DocumentOutput:
    total_pages = len(pages)
    total_sections = sum(len(p.sections) for p in pages)
    total_tables = sum(len(p.tables) for p in pages)
    errors = sum(1 for p in pages if p.error)
    doc = DocumentOutput(
        filename=filename,
        pages=pages,
        processing_time_seconds=round(elapsed, 2),
    )
    logger.info(
        "Document %s: %d pages, %d sections, %d tables, %d errors in %.1fs",
        filename,
        total_pages,
        total_sections,
        total_tables,
        errors,
        elapsed,
    )
    return doc
