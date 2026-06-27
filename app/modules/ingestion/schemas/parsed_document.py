from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)


class ParsedDocument(
    BaseModel
):

    model_config = ConfigDict(
        from_attributes=True
    )

    document_id: UUID | None = None

    source_document_id: int | None = None

    ingestion_job_id: int | None = None

    dataset_id: int | None = None

    corpus_source_id: int | None = None

    file_name: str

    file_extension: str

    mime_type: str

    parser_code: str

    title: str | None = None

    language: str | None = None

    page_count: int | None = None

    character_count: int = 0

    text_content: str

    metadata: dict = Field(
        default_factory=dict
    )

    extracted_at: datetime = Field(
        default_factory=datetime.utcnow
    )