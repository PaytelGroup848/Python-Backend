from pydantic import BaseModel


class TrainingResult(
    BaseModel
):

    success: bool

    training_job_id: int

    artifact_path: str | None = None

    message: str