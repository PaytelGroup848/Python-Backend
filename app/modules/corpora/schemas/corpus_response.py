from datetime import datetime

from pydantic import BaseModel


class CorpusResponse(
    BaseModel
):

    id: int

    name: str

    domain: str

    description: str | None = None

    status: str

    created_at: datetime

    updated_at: datetime

    model_config = {
        "from_attributes": True
    }