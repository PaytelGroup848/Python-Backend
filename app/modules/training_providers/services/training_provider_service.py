from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.training_providers.models.training_provider import (
    TrainingProvider
)

from app.modules.training_providers.repositories.training_provider_repository import (
    training_provider_repository
)


class TrainingProviderService:

    async def create_provider(

        self,

        db: AsyncSession,

        data: dict

    ):

        provider = TrainingProvider(
            **data
        )

        return await (
            training_provider_repository
            .create(
                db,
                provider
            )
        )

    async def get_provider(

        self,

        db: AsyncSession,

        provider_id: int

    ):

        return await (
            training_provider_repository
            .get_by_id(
                db,
                provider_id
            )
        )

    async def get_by_code(

        self,

        db: AsyncSession,

        code: str

    ):

        return await (
            training_provider_repository
            .get_by_code(
                db,
                code
            )
        )

    async def list_active(

        self,

        db: AsyncSession

    ):

        return await (
            training_provider_repository
            .list_active(
                db
            )
        )


training_provider_service = (
    TrainingProviderService()
)