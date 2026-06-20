from pydantic import BaseModel


class ModelReleaseCreate(
    BaseModel
):

    promotion_id: int

    release_version: str

    release_name: str

    release_notes: str | None = None

    release_status: str = "draft"

    created_by: str | None = None