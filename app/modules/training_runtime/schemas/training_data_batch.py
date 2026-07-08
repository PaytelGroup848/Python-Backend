from pydantic import (
    BaseModel,
    Field,
)

from app.modules.training_runtime.schemas.training_data_record import (
    TrainingDataRecord,
)


class TrainingDataBatch(
    BaseModel
):

    records: list[
        TrainingDataRecord
    ] = Field(
        default_factory=list
    )

    first_record_id: int

    last_record_id: int

    record_count: int