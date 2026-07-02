from datetime import datetime

from pydantic import BaseModel

from app.shared.constants.organization_status import (
    OrganizationStatus
)

from app.shared.constants.organization_type import (
    OrganizationType
)


class OrganizationResponse(
    BaseModel
):

    id: int

    code: str

    name: str

    slug: str

    description: str | None

    logo_url: str | None

    website: str | None

    email: str | None

    phone: str | None

    country: str | None

    timezone: str | None

    organization_type: OrganizationType

    status: OrganizationStatus

    is_system: bool

    is_active: bool

    created_at: datetime

    updated_at: datetime

    class Config:

        from_attributes = True