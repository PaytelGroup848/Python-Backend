from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class LocalFilesystemStorageConfiguration(
    BaseModel
):

    model_config = ConfigDict(
        extra="forbid"
    )

    root_directory: str = Field(
        min_length=1
    )