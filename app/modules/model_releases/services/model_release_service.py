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

        return await (
            model_release_repository
            .create(
                db,
                release
            )
        )

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


model_release_service = (
    ModelReleaseService()
)