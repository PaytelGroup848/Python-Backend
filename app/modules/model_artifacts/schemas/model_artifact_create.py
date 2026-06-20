from pydantic import BaseModel


class ModelArtifactCreate(
    BaseModel
):

    training_job_id: int

    artifact_name: str

    artifact_path: str

    artifact_type: str

    size_bytes: int | None = None

    checksum: str | None = None