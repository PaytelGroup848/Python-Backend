from datetime import datetime

from pydantic import BaseModel


class DatasetSnapshotResponse(
    BaseModel,
):

    id: int

    dataset_id: int

    snapshot_code: str

    status: str

    record_count: int

    max_record_id: int | None

    content_hash: str

    snapshot_metadata_json: dict

    is_immutable: bool

    frozen_at: datetime

    created_at: datetime

    class Config:

        from_attributes = True