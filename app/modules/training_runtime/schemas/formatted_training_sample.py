from pydantic import (
    BaseModel,
    Field,
)


class FormattedTrainingSample(
    BaseModel
):

    source_record_id: int

    formatter_code: str

    input_text: str

    target_text: str | None = None

    metadata: dict = Field(
        default_factory=dict
    )