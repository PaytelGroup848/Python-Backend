from pydantic import (
    BaseModel,
    Field,
)


class TokenizedTrainingSample(
    BaseModel
):

    source_record_id: int

    input_ids: list[int]

    attention_mask: list[int]

    labels: list[int]

    metadata: dict = Field(
        default_factory=dict
    )