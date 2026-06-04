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
                ModelRegistry.model_name
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
                ModelRegistry.is_active
                == True
            )
        )

        return (
            result.scalars()
            .all()
        )
    async def get_by_name(
        self,
        db: AsyncSession,
        model_name: str
    ):

        result = await db.execute(

            select(ModelRegistry)

            .where(
                ModelRegistry.model_name
                == model_name
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