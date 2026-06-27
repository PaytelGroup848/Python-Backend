from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)


class NLPSentence(
    BaseModel
):

    model_config = ConfigDict(
        from_attributes=True
    )

    text: str

    start_offset: int

    end_offset: int


class NLPDocument(
    BaseModel
):

    model_config = ConfigDict(
        from_attributes=True
    )

    text: str

    language: str | None = None

    metadata: dict = Field(
        default_factory=dict
    )

    sentences: list[
        NLPSentence
    ] = Field(
        default_factory=list
    )