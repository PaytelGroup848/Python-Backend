from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from fastapi import (
    HTTPException,
    status
)

from app.modules.organizations.models.organization import (
    Organization
)

from app.modules.organizations.repositories.organization_repository import (
    organization_repository
)

from app.modules.organizations.schemas.organization_create import (
    OrganizationCreate
)

from app.modules.organizations.schemas.organization_update import (
    OrganizationUpdate
)


class OrganizationService:

    async def create_organization(

        self,

        db: AsyncSession,

        data: OrganizationCreate,

        created_by: str | None = None

    ):

        existing_code = await (
            organization_repository
            .get_by_code(
                db=db,
                code=data.code
            )
        )

        if existing_code:

            raise HTTPException(

                status_code=status.HTTP_409_CONFLICT,

                detail="Organization code already exists"
            )

        existing_slug = await (
            organization_repository
            .get_by_slug(
                db=db,
                slug=data.slug
            )
        )

        if existing_slug:

            raise HTTPException(

                status_code=status.HTTP_409_CONFLICT,

                detail="Organization slug already exists"
            )

        organization = Organization(

            **data.model_dump(),

            created_by=created_by

        )

        organization = await (

            organization_repository
            .create(
                db=db,
                organization=organization
            )

        )

        await db.commit()

        await db.refresh(
            organization
        )

        return organization

    async def get_organization(

        self,

        db: AsyncSession,

        organization_id: int

    ):

        return await (

            organization_repository
            .get_by_id(
                db=db,
                organization_id=organization_id
            )

        )

    async def get_by_code(

        self,

        db: AsyncSession,

        code: str

    ):

        return await (

            organization_repository
            .get_by_code(
                db=db,
                code=code
            )

        )

    async def get_by_slug(

        self,

        db: AsyncSession,

        slug: str

    ):

        return await (

            organization_repository
            .get_by_slug(
                db=db,
                slug=slug
            )

        )

    async def list_organizations(

        self,

        db: AsyncSession

    ):

        return await (

            organization_repository
            .list(
                db=db
            )

        )

    async def update_organization(

        self,

        db: AsyncSession,

        organization: Organization,

        data: OrganizationUpdate

    ):

        update_data = (

            data.model_dump(
                exclude_unset=True
            )

        )

        for key, value in update_data.items():

            setattr(
                organization,
                key,
                value
            )

        organization = await (

            organization_repository
            .update(
                db=db,
                organization=organization
            )

        )

        await db.commit()

        await db.refresh(
            organization
        )

        return organization


organization_service = (
    OrganizationService()
)