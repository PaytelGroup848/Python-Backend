from pydantic import (
    BaseModel,
    Field,
)


class DatasetCreate(
    BaseModel
):

    corpus_id: int = Field(
        gt=0,
    )

    name: str = Field(
        min_length=1,
        max_length=255,
    )

    domain: str = Field(
        min_length=1,
        max_length=100,
    )

    version: str = Field(
        min_length=1,
        max_length=50,
    )

    description: str | None = None

    source: str | None = None