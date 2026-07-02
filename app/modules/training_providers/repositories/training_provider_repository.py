from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.training_providers.models.training_provider import (
    TrainingProvider
)


class TrainingProviderRepository:

    async def create(

        self,

        db: AsyncSession,

        provider: TrainingProvider

    ):

        db.add(provider)

        await db.flush()

        await db.refresh(
            provider
        )

        return provider
    
    async def update(

        self,

        db: AsyncSession,

        provider: TrainingProvider

    ):

        await db.flush()

        await db.refresh(
            provider
        )

        return provider
    
    async def delete(

        self,

        db: AsyncSession,

        provider: TrainingProvider

    ):

        await db.delete(
            provider
        )

    async def get_by_id(

        self,

        db: AsyncSession,

        provider_id: int

    ):

        result = await db.execute(

            select(
                TrainingProvider
            )
            .where(
                TrainingProvider.id
                ==
                provider_id
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
                TrainingProvider
            )
            .where(
                TrainingProvider.code
                ==
                code
            )
        )

        return result.scalar_one_or_none()
    
    async def list_all(

        self,

        db: AsyncSession

    ):

        result = await db.execute(

            select(
                TrainingProvider
            )

            .order_by(
                TrainingProvider.display_name
            )

        )

        return result.scalars().all()

    async def list_active(

        self,

        db: AsyncSession

    ):

        result = await db.execute(

            select(
                TrainingProvider
            )
            .where(
                TrainingProvider.is_active.is_(True)
            )
        )

        return result.scalars().all()
    
    async def list_by_runtime_type(

        self,

        db: AsyncSession,

        runtime_type: str

    ):

        result = await db.execute(

            select(
                TrainingProvider
            )

            .where(
                TrainingProvider.runtime_type
                ==
                runtime_type
            )

            .order_by(
                TrainingProvider.display_name
            )

        )

        return result.scalars().all()

    


training_provider_repository = (
    TrainingProviderRepository()
)