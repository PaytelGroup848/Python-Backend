from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PipelineRunResponse(
    BaseModel
):

    id: int

    pipeline_id: int

    dataset_id: Optional[int] = None

    corpus_source_id: Optional[int] = None

    run_code: str

    trigger_type: str

    status: str

    metrics_json: Optional[dict] = None

    started_at: datetime

    completed_at: Optional[datetime] = None

    error_message: Optional[str] = None

    created_at: datetime

    updated_at: datetime

    class Config:

        from_attributes = True