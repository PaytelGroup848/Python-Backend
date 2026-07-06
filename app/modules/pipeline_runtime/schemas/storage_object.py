from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class StorageObject(
    BaseModel
):

    model_config = ConfigDict(
        extra="forbid"
    )

    storage_provider: str

    storage_reference: str

    mime_type: str | None = None

    size_bytes: int | None = None

    checksum: str | None = None

    metadata: dict = Field(
        default_factory=dict
    )