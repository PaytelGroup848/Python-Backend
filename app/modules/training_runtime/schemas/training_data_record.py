from pydantic import (
    BaseModel,
    Field,
)


class TrainingDataRecord(
    BaseModel
):

    record_id: int

    dataset_id: int

    record_type: str

    input_text: str

    output_text: str | None = None

    metadata: dict = Field(
        default_factory=dict
    )