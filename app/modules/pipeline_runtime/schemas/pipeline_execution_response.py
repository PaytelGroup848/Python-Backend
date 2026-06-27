from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict
)


class PipelineExecutionResponse(
    BaseModel
):

    model_config = ConfigDict(
        from_attributes=True
    )

    pipeline_run_id: int

    run_code: str

    status: str

    started_at: datetime