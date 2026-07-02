from pydantic import (
    BaseModel,
    Field
)


class WorkspaceAssistantCreate(
    BaseModel
):

    workspace_id: int

    assistant_id: int

    priority: int = Field(
        default=100,
        ge=1
    )

    is_default: bool = False

    is_active: bool = True