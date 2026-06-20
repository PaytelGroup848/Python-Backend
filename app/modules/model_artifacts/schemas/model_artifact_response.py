from datetime import datetime

from pydantic import BaseModel


class ModelArtifactResponse(
    BaseModel
):

    id: int

    training_job_id: int

    artifact_name: str

    artifact_path: str

    artifact_type: str

    size_bytes: int | None

    checksum: str | None

    created_at: datetime

    class Config:

        from_attributes = True