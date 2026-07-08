from pydantic import (
    BaseModel,
    Field,
)


class TrainingRuntime(
    BaseModel
):

    training_job_id: int

    dataset_id: int

    dataset_snapshot_id: int

    snapshot_record_count: int

    snapshot_max_record_id: int | None

    snapshot_content_hash: str

    provider_id: int

    provider_code: str

    runtime_type: str

    runtime_code: str

    runtime_class: str

    runtime_version: str | None = None

    base_model_id: int

    base_model_code: str

    base_model_version_id: int

    base_model_version: str

    base_model_source_type: str

    base_model_source_uri: str

    base_model_source_revision: str | None = None

    training_configuration_id: int

    training_type: str

    runtime_configuration: dict = Field(
        default_factory=dict
    )

    capabilities: dict = Field(
        default_factory=dict
    )

    status: str

    artifact_directory: str | None = None