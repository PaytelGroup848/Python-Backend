from pydantic import (
    BaseModel,
    Field
)


class TrainingRuntime(
    BaseModel
):

    training_job_id: int

    dataset_id: int

    provider_id: int

    provider_code: str

    runtime_type: str

    runtime_code: str

    runtime_version: str | None = None

    base_model_id: int

    base_model_code: str

    training_type: str

    runtime_configuration: dict = Field(
        default_factory=dict
    )

    capabilities: dict = Field(
        default_factory=dict
    )

    status: str

    artifact_directory: str | None = None