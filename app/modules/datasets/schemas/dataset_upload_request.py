from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class DatasetUploadRequest(
    BaseModel,
):

    model_config = ConfigDict(
        extra="forbid",
    )

    dataset_id: int = Field(
        gt=0,
    )

    original_file_name: str = Field(
        min_length=1,
        max_length=500,
    )

    mime_type: str = Field(
        min_length=1,
        max_length=255,
    )

    file_size: int = Field(
        gt=0,
    )

    content: bytes

    created_by: str | None = Field(
        default=None,
        max_length=255,
    )

    metadata_json: dict | None = Field(
        default=None,
    )