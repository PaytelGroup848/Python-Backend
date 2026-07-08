from typing import Any

from pydantic import BaseModel


class DataPipelineStepUpdate(
    BaseModel
):

    step_order: int | None = None

    step_code: str | None = None

    step_type: str | None = None

    runtime_code: str | None = None

    output_storage_instance_id: int | None = None

    configuration_json: (
        dict[str, Any] | None
    ) = None

    status: str | None = None