from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class KnowledgeBaseCreate(BaseModel):

    name: str

    code: str

    description: str | None = None


class KnowledgeBaseResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    name: str

    code: str

    description: str | None = None

    is_active: bool

    created_at: datetime

    updated_at: datetime