from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.organizations.models.organization import (
    Organization
)


class OrganizationRepository:

    async def create(

        self,

        db: AsyncSession,

        organization: Organization

    ):

        db.add(
            organization
        )

        await db.flush()

        await db.refresh(
            organization
        )

        return organization

    async def get_by_id(

        self,

        db: AsyncSession,

        organization_id: int

    ):

        result = await db.execute(

            select(
                Organization
            )
            .where(
                Organization.id
                ==
                organization_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_code(

        self,

        db: AsyncSession,

        code: str

    ):

        result = await db.execute(

            select(
                Organization
            )
            .where(
                Organization.code
                ==
                code
            )
        )

        return result.scalar_one_or_none()

    async def get_by_slug(

        self,

        db: AsyncSession,

        slug: str

    ):

        result = await db.execute(

            select(
                Organization
            )
            .where(
                Organization.slug
                ==
                slug
            )
        )

        return result.scalar_one_or_none()

    async def list(

        self,

        db: AsyncSession

    ):

        result = await db.execute(

            select(
                Organization
            )
        )

        return result.scalars().all()

    async def update(

        self,

        db: AsyncSession,

        organization: Organization

    ):

        await db.flush()

        await db.refresh(
            organization
        )

        return organization


organization_repository = (
    OrganizationRepository()
)