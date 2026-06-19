from slm_pdf.models import PageContent, DocumentOutput, SectionContent, TableContent


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
    return PageContent(
        page_number=page_number,
        sections=sections,
        tables=tables,
        metadata=data.get("metadata", {}),
        raw_text=data.get("raw_text", ""),
        error=data.get("error"),
    )


def assemble_document(
    pages: list[PageContent], filename: str, elapsed: float
) -> DocumentOutput:
    return DocumentOutput(
        filename=filename,
        pages=pages,
        processing_time_seconds=round(elapsed, 2),
    )
