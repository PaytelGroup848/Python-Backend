from datetime import datetime

from pydantic import BaseModel


class TrainingJobResponse(
    BaseModel
):

    id: int

    dataset_id: int

    base_model: str

    training_type: str

    status: str

    artifact_path: str | None

    started_at: datetime | None

    completed_at: datetime | None

    created_at: datetime

    class Config:

        from_attributes = True