from datetime import datetime
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
)


class EvaluationJobResponse(
    BaseModel
):

    id: int

    artifact_id: int

    dataset_version_id: int

    evaluation_type: str

    status: str

    runtime_configuration: dict[str, Any]

    metrics: dict[str, Any]

    summary: dict[str, Any]

    started_at: datetime | None

    completed_at: datetime | None

    duration_ms: float | None

    failure_reason: str | None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )