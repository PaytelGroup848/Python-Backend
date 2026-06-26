from datetime import datetime
from typing import Any

from pydantic import BaseModel


class DatasetRecordResponse(
    BaseModel
):

    id: int

    dataset_id: int

    corpus_source_id: int | None = None

    record_type: str

    status: str

    record_hash: str

    validation_score: int | None = None

    input_text: str

    output_text: str | None = None

    metadata_json: dict[str, Any] | None = None

    created_at: datetime

    updated_at: datetime

    class Config:

        from_attributes = True