from datetime import datetime

from pydantic import (
    BaseModel
)


class WorkspaceResponse(
    BaseModel
):

    id: int

    organization_id: int

    code: str

    name: str

    slug: str

    description: str | None

    icon_url: str | None

    is_system: bool

    is_public: bool

    is_active: bool

    created_by: str | None

    created_at: datetime

    updated_at: datetime

    class Config:

        from_attributes = True