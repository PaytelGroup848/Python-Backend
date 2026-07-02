from pydantic import (
    BaseModel
)


class WorkspaceAssistantUpdate(
    BaseModel
):

    priority: int | None = None

    is_default: bool | None = None

    is_active: bool | None = None