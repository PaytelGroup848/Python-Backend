from pydantic import BaseModel


class TrainingRuntime(
    BaseModel
):

    training_job_id: int

    dataset_id: int

    provider_id: int

    provider_code: str

    provider_type: str

    base_model: str

    training_type: str

    status: str

    artifact_path: str | None = None