from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.models.model import (
    ModelRegistry
)


class ModelRepository:

    async def create(
        self,
        db: AsyncSession,
        model: ModelRegistry
    ):

        db.add(model)

        await db.commit()

        await db.refresh(model)

        return model

    async def get_models(
        self,
        db: AsyncSession
    ):

        result = await db.execute(

            select(ModelRegistry)

            .order_by(
                ModelRegistry.display_name
            )
        )

        return (
            result.scalars()
            .all()
        )

    async def get_active_models(
        self,
        db: AsyncSession
    ):

        result = await db.execute(

            select(ModelRegistry)

            .where(
                ModelRegistry.is_active.is_(True)
            )
        )

        return (
            result.scalars()
            .all()
        )
    async def get_by_code(
        self,
        db: AsyncSession,
        code: str
    ):

        result = await db.execute(

            select(ModelRegistry)

            .where(
                ModelRegistry.code == code
            )
        )

        return (
            result.scalar_one_or_none()
        )
    
    async def update(
        self,
        db: AsyncSession,
        model: ModelRegistry
    ):

        await db.commit()

        await db.refresh(
            model
        )

        return model
    
    async def delete(
        self,
        db: AsyncSession,
        model: ModelRegistry
    ):

        await db.delete(
            model
        )

        await db.commit()

    async def get_by_id(
        self,
        db: AsyncSession,
        model_id: int
    ):

        result = await db.execute(

            select(ModelRegistry)

            .where(
                ModelRegistry.id == model_id
            )

        )

        return result.scalar_one_or_none()
    
    async def exists_by_code(
        self,
        db: AsyncSession,
        code: str
    ) -> bool:

        result = await db.execute(
 
            select(ModelRegistry.id)

            .where(
                ModelRegistry.code == code
            )

        )

        return result.scalar_one_or_none() is not None
    
    async def get_by_status(
        self,
        db: AsyncSession,
        status: str
    ):

        result = await db.execute(
 
            select(ModelRegistry)

            .where(
                ModelRegistry.status == status
            )

            .order_by(
                ModelRegistry.display_name
            )

        )

        return result.scalars().all()
    
    async def get_by_provider(
        self,
        db: AsyncSession,
        provider_id: int
    ):

        result = await db.execute(

            select(ModelRegistry)

            .where(
                ModelRegistry.provider_id == provider_id
            )

            .order_by(
                ModelRegistry.display_name
            )

        )

        return result.scalars().all()