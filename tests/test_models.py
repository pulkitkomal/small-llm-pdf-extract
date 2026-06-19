from slm_pdf.models import DocumentOutput, PageContent, SectionContent, TableContent


def test_page_content_defaults():
    page = PageContent(page_number=1)
    assert page.sections == []
    assert page.tables == []
    assert page.error is None


def test_document_output_roundtrip():
    doc = DocumentOutput(
        filename="test.pdf",
        pages=[
            PageContent(
                page_number=1,
                sections=[SectionContent(heading="Intro", content="Hello")],
                tables=[TableContent(headers=["A"], rows=[["1"]])],
                metadata={"key": "val"},
            )
        ],
        processing_time_seconds=10.5,
    )
    data = doc.model_dump()
    assert data["filename"] == "test.pdf"
    assert data["pages"][0]["sections"][0]["heading"] == "Intro"
    restored = DocumentOutput.model_validate(data)
    assert restored == doc


def test_page_content_error():
    page = PageContent(page_number=1, error="Something went wrong")
    assert page.error == "Something went wrong"
    assert page.sections == []
