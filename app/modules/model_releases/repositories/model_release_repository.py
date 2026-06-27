from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.model_releases.models.model_release import (
    ModelRelease
)


class ModelReleaseRepository:

    async def create(

        self,

        db: AsyncSession,

        release: ModelRelease

    ):

        db.add(release)

        await db.flush()

        await db.refresh(release)

        return release
    
    async def update(

        self,

        db: AsyncSession,

        release: ModelRelease

    ):

        await db.flush()

        await db.refresh(
            release
        )

        return release
    
    async def delete(

        self,

        db: AsyncSession,

        release: ModelRelease

    ):

        await db.delete(
            release
        )

    async def get_by_id(

        self,

        db: AsyncSession,

        release_id: int

    ):

        result = await db.execute(

            select(
                ModelRelease
            )
            .where(
                ModelRelease.id
                ==
                release_id
            )
        )

        return result.scalar_one_or_none()
    
    async def get_by_version(

        self,

        db: AsyncSession,

        release_version: str

    ):

        result = await db.execute(

            select(
                ModelRelease
            )

            .where(
                ModelRelease.release_version
                ==
                release_version
            )

        )

        return result.scalar_one_or_none()
    
    async def get_default_release(

        self,

        db: AsyncSession

    ):

        result = await db.execute(

            select(
                ModelRelease
            )

            .where(
                ModelRelease.is_default.is_(True)
            )

        )

        return result.scalar_one_or_none()
    
    async def list_by_status(

        self,

        db: AsyncSession,

        release_status: str

    ):

        result = await db.execute(

            select(
                ModelRelease
            )

            .where(
                ModelRelease.release_status
                ==
                release_status
            )

            .order_by(
                ModelRelease.created_at.desc()
            )

        )

        return result.scalars().all()

    async def list_all(

        self,

        db: AsyncSession

    ):

        result = await db.execute(

            select(
                ModelRelease
            )

            .order_by(
                ModelRelease.created_at.desc()
            )

        )

        return result.scalars().all()


model_release_repository = (
    ModelReleaseRepository()
)