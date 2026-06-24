from datetime import datetime

from pydantic import BaseModel


class CorpusSourceResponse(
    BaseModel
):

    id: int

    corpus_id: int

    source_type: str

    source_reference: str

    status: str

    created_at: datetime

    updated_at: datetime

    class Config:

        from_attributes = True