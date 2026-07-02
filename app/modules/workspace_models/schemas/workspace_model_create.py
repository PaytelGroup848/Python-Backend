from pydantic import (
    BaseModel,
    Field
)


class WorkspaceModelCreate(
    BaseModel
):

    workspace_id: int

    model_release_id: int

    is_default: bool = False

    is_active: bool = True

    priority: int = Field(
        default=100,
        ge=1
    )