from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PipelineStepRunResponse(
    BaseModel
):

    id: int

    pipeline_run_id: int

    pipeline_step_id: int

    step_run_code: str

    execution_order: int

    status: str

    metrics_json: Optional[dict] = None

    started_at: Optional[datetime] = None

    completed_at: Optional[datetime] = None

    error_message: Optional[str] = None

    created_at: datetime

    updated_at: datetime

    class Config:

        from_attributes = True