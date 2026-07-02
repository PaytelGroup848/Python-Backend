from pydantic import (
    BaseModel,
    EmailStr,
    HttpUrl
)

from app.shared.constants.organization_type import (
    OrganizationType
)


class OrganizationUpdate(
    BaseModel
):

    name: str | None = None

    description: str | None = None

    logo_url: HttpUrl | None = None

    website: HttpUrl | None = None

    email: EmailStr | None = None

    phone: str | None = None

    country: str | None = None

    timezone: str | None = None

    organization_type: OrganizationType | None = None