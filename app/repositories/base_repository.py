from typing import Generic, TypeVar, Type, Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get_by_id(
        self,
        db: AsyncSession,
        entity_id: int
    ) -> Optional[ModelType]:

        result = await db.execute(
            select(self.model).where(self.model.id == entity_id)
        )

        return result.scalar_one_or_none()

    async def get_all(
        self,
        db: AsyncSession
    ) -> List[ModelType]:

        result = await db.execute(select(self.model))

        return result.scalars().all()

    async def create(
        self,
        db: AsyncSession,
        obj
    ) -> ModelType:

        db.add(obj)

        await db.commit()

        await db.refresh(obj)

        return obj

    async def delete(
        self,
        db: AsyncSession,
        obj: ModelType
    ):

        await db.delete(obj)

        await db.commit()