from datetime import datetime

from pydantic import BaseModel


class ModelReleaseResponse(
    BaseModel
):

    id: int

    promotion_id: int

    release_version: str

    release_name: str

    release_notes: str | None

    release_status: str

    created_by: str | None

    created_at: datetime

    class Config:

        from_attributes = True