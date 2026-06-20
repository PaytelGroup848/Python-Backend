from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class AssistantKnowledgeBaseCreate(
    BaseModel
):

    

    knowledge_base_id: int


class AssistantKnowledgeBaseResponse(
    BaseModel
):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    assistant_id: int

    knowledge_base_id: int

    is_active: bool

    created_at: datetime

    updated_at: datetime