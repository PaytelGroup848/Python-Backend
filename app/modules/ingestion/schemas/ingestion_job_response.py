from datetime import datetime

from pydantic import BaseModel


class IngestionJobResponse(
    BaseModel
):

    id: int

    corpus_source_id: int

    dataset_id: int | None = None

    status: str

    records_processed: int

    error_message: str | None = None

    created_at: datetime

    updated_at: datetime

    completed_at: datetime | None = None

    class Config:

        from_attributes = True