from pydantic import (
    BaseModel,
    Field
)


class TrainingResult(
    BaseModel
):

    success: bool

    training_job_id: int

    runtime_code: str

    model_version_id: int | None = None

    artifact_directory: str | None = None

    metrics: dict = Field(
        default_factory=dict
    )

    runtime_metadata: dict = Field(
        default_factory=dict
    )

    message: str