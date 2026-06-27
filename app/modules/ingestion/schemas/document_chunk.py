from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)


class DocumentChunk(
    BaseModel
):

    model_config = ConfigDict(
        from_attributes=True
    )

    chunk_id: UUID | None = None

    source_document_id: int | None = None

    dataset_id: int | None = None

    corpus_source_id: int | None = None

    chunk_index: int

    content: str

    character_count: int

    token_count: int

    start_offset: int

    end_offset: int

    metadata: dict = Field(
        default_factory=dict
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )