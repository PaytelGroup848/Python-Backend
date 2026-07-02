from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.training_providers.models.training_provider import (
    TrainingProvider
)

from app.modules.training_providers.repositories.training_provider_repository import (
    training_provider_repository
)

from app.modules.training_providers.schemas.training_provider_create import (
    TrainingProviderCreate
)

class TrainingProviderService:

    async def create_provider(

        self,

        db: AsyncSession,

        data: TrainingProviderCreate

    ):

        provider = TrainingProvider(
            **data.model_dump()
        )

        provider = await (
            training_provider_repository
            .create(
                db=db,
                provider=provider
            )
        )

        await db.commit()

        return provider

    async def get_provider(

        self,

        db: AsyncSession,

        provider_id: int

    ):

        return await (
            training_provider_repository
            .get_by_id(
                db=db,
                provider_id=provider_id
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
                db=db,
                code=code
            )
        )
    
    async def list_all(

        self,

        db: AsyncSession

    ):

        return await (
            training_provider_repository
            .list_all(
                db=db
            )
        )

    async def list_active(

        self,

        db: AsyncSession

    ):

        return await (
            training_provider_repository
            .list_active(
                db=db
            )
        )
    
    async def list_by_runtime_type(

        self,

        db: AsyncSession,

        runtime_type: str

    ):

        return await (
            training_provider_repository
            .list_by_runtime_type(
                db=db,
                runtime_type=runtime_type
            )
        )
    
    async def update_provider(

        self,

        db: AsyncSession,

        provider: TrainingProvider

    ):

        provider = await (
            training_provider_repository
            .update(
                db=db,
                provider=provider
            )
        )

        await db.commit()

        return provider
    
    async def delete_provider(

        self,

        db: AsyncSession,

        provider_id: int

    ) -> bool:

        provider = await (
            training_provider_repository
            .get_by_id(
                db=db,
                provider_id=provider_id
            )
        )

        if provider is None:

            return False

        await (
            training_provider_repository
            .delete(
                db=db,
                provider=provider
            )
        )

        await db.commit()

        return True
  
training_provider_service = (
    TrainingProviderService()
)