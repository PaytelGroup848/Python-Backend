from typing import Optional

from pydantic import BaseModel


class DataPipelineCreate(
    BaseModel
):

    corpus_id: int

    name: str

    pipeline_code: str

    dataset_id: Optional[int] = None

    status: str