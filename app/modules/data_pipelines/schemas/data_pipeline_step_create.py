from typing import Any

from pydantic import BaseModel


class DataPipelineStepCreate(
    BaseModel
):

    pipeline_id: int

    step_order: int

    step_code: str

    step_type: str

    runtime_code: str

    configuration_json: dict[str, Any] | None = None

    status: str