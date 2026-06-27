from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict
)


class ModelReleaseResponse(
    BaseModel
):

    id: int

    promotion_id: int

    release_version: str

    release_name: str

    release_notes: str | None

    checksum: str | None

    release_status: str

    is_default: bool

    created_by: str | None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )