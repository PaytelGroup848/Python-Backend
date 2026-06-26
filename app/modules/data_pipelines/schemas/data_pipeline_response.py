from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DataPipelineResponse(
    BaseModel
):

    id: int

    corpus_id: int

    name: str

    pipeline_code: str

    dataset_id: Optional[int] = None

    status: str

    created_at: datetime

    updated_at: datetime

    class Config:

        from_attributes = True