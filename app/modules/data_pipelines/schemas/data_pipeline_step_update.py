from typing import Optional

from pydantic import BaseModel


class DataPipelineStepUpdate(
    BaseModel
):

    step_order: Optional[int] = None

    step_type: Optional[str] = None

    runtime_code: Optional[str] = None

    configuration_json: Optional[str] = None

    status: Optional[str] = None