from typing import Optional

from pydantic import BaseModel


class PipelineRunCreate(
    BaseModel
):

    pipeline_id: int

    dataset_id: Optional[int] = None

    corpus_source_id: Optional[int] = None

    run_code: str

    trigger_type: str

    status: str

    metrics_json: Optional[dict] = None

    error_message: Optional[str] = None