from typing import Optional

from pydantic import BaseModel


class PipelineStepRunCreate(
    BaseModel
):

    pipeline_run_id: int

    pipeline_step_id: int

    step_run_code: str

    execution_order: int

    status: str

    metrics_json: Optional[dict] = None

    error_message: Optional[str] = None