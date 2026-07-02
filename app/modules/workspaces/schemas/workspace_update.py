from pydantic import (
    BaseModel
)


class WorkspaceUpdate(
    BaseModel
):

    name: str | None = None

    description: str | None = None

    icon_url: str | None = None