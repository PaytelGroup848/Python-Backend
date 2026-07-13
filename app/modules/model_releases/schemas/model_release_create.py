from pydantic import BaseModel


class ModelReleaseCreate(
    BaseModel
):
    
    model_version_id: int

    promotion_id: int

    release_version: str

    release_name: str

    release_notes: str | None = None

    checksum: str | None = None

    release_status: str = "DRAFT"

    is_default: bool = False

    created_by: str | None = None