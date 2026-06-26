from typing import Any

from pydantic import BaseModel


class DatasetRecordCreate(
    BaseModel
):

    dataset_id: int

    corpus_source_id: int | None = None

    record_type: str

    status: str

    input_text: str

    output_text: str | None = None

    metadata_json: dict[str, Any] | None = None