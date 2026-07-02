from pydantic import BaseModel


class WorkspaceCreate(
    BaseModel
):

    code: str

    name: str

    slug: str

    description: str | None = None

    icon_url: str | None = None