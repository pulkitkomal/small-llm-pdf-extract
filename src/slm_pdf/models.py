from pydantic import BaseModel
from typing import Optional


class SectionContent(BaseModel):
    heading: str = ""
    content: str = ""


class TableContent(BaseModel):
    headers: list[str] = []
    rows: list[list[str]] = []


class PageContent(BaseModel):
    page_number: int
    sections: list[SectionContent] = []
    tables: list[TableContent] = []
    metadata: dict[str, str] = {}
    raw_text: str = ""
    error: Optional[str] = None


class DocumentOutput(BaseModel):
    filename: str
    pages: list[PageContent] = []
    processing_time_seconds: float = 0.0
