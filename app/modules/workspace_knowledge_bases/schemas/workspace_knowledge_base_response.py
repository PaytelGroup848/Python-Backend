from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict
)


class WorkspaceKnowledgeBaseResponse(
    BaseModel
):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    workspace_id: int

    knowledge_base_id: int

    priority: int

    is_default: bool

    is_active: bool

    created_at: datetime

    updated_at: datetime