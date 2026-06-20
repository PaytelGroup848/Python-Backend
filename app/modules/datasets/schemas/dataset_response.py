from datetime import datetime

from pydantic import BaseModel


class DatasetResponse(
    BaseModel
):

    id: int

    name: str

    domain: str

    version: str

    description: str | None

    source: str | None

    record_count: int

    status: str

    created_at: datetime

    class Config:

        from_attributes = True