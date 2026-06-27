from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.model_releases.models.model_release import (
    ModelRelease
)

from app.modules.model_releases.repositories.model_release_repository import (
    model_release_repository
)

from app.modules.model_releases.schemas.model_release_create import (
    ModelReleaseCreate
)


class ModelReleaseService:

    async def create_release(

        self,

        db: AsyncSession,

        data: ModelReleaseCreate

    ):

        release = ModelRelease(
            **data.model_dump()
        )

        release = await (
            model_release_repository
            .create(
                db=db,
                release=release
            )
        )

        return release

    async def get_release(

        self,

        db: AsyncSession,

        release_id: int

    ):

        return await (
            model_release_repository
            .get_by_id(
                db,
                release_id
            )
        )
    
    async def list_releases(

        self,

        db: AsyncSession

    ):

        return await (
            model_release_repository
            .list_all(
                db=db
            )
        )
    
    async def get_release_by_version(

        self,

        db: AsyncSession,

        release_version: str

    ):

        return await (
            model_release_repository
            .get_by_version(
                db=db,
                release_version=release_version
            )
        )
    
    async def list_releases_by_status(

        self,

        db: AsyncSession,

        release_status: str

    ):

        return await (
            model_release_repository
            .list_by_status(
                db=db,
                release_status=release_status
            )
        )
    
    async def get_default_release(

        self,

        db: AsyncSession

    ):

        return await (
            model_release_repository
            .get_default_release(
                db=db
            )
        )
    
    async def update_release(

        self,

        db: AsyncSession,

        release: ModelRelease

    ):

        return await (
            model_release_repository
            .update(
                db=db,
                release=release
            )
        )
    
    async def delete_release(

        self,

        db: AsyncSession,

        release_id: int

    ) -> bool:

        release = await (
            model_release_repository
            .get_by_id(
                db=db,
                release_id=release_id
            )
        )

        if release is None:

            return False

        await (
            model_release_repository
            .delete(
                db=db,
                release=release
            )
        )

        return True


model_release_service = (
    ModelReleaseService()
)