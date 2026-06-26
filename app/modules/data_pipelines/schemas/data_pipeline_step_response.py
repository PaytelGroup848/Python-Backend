from datetime import datetime
from typing import Any

from pydantic import BaseModel


class DataPipelineStepResponse(
    BaseModel
):

    id: int

    pipeline_id: int

    step_order: int

    step_code: str

    step_type: str

    runtime_code: str

    configuration_json: dict[str, Any] | None = None

    status: str

    created_at: datetime

    updated_at: datetime

    class Config:

        from_attributes = True