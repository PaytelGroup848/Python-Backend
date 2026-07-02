from dataclasses import dataclass

from app.models.user import User

from app.modules.organizations.models.organization import (
    Organization
)

from app.modules.workspaces.models.workspace import (
    Workspace
)


@dataclass(slots=True)
class RequestContext:

    user: User

    organization: Organization

    workspace: Workspace | None = None