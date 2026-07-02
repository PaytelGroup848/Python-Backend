from pydantic import (
    BaseModel,
    EmailStr,
    HttpUrl
)

from app.shared.constants.organization_type import (
    OrganizationType
)


class OrganizationCreate(
    BaseModel
):

    code: str

    name: str

    slug: str

    description: str | None = None

    logo_url: HttpUrl | None = None

    website: HttpUrl | None = None

    email: EmailStr | None = None

    phone: str | None = None

    country: str | None = None

    timezone: str | None = None

    organization_type: OrganizationType = (
        OrganizationType.PERSONAL
    )