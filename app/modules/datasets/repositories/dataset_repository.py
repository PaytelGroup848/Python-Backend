from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.datasets.models.dataset import (
    Dataset
)


class DatasetRepository:

    async def create(
        self,
        db: AsyncSession,
        dataset: Dataset
    ):

        db.add(dataset)

        await db.flush()

        await db.refresh(dataset)

        return dataset

    async def get_by_id(
        self,
        db: AsyncSession,
        dataset_id: int
    ):

        result = await db.execute(
            select(Dataset)
            .where(
                Dataset.id == dataset_id
            )
        )

        return result.scalar_one_or_none()
    
    async def get_by_id_for_update(
        self,
        db: AsyncSession,
        dataset_id: int,
    ):

        result = await db.execute(
            select(
                Dataset
            )
            .where(
                Dataset.id
                ==
                dataset_id
            )
            .with_for_update()
        )

        return result.scalar_one_or_none()
    
    async def update(
        self,
        db: AsyncSession,
        dataset: Dataset,
    ):

        await db.flush()

        await db.refresh(
            dataset
        )

        return dataset

    async def list_all(
        self,
        db: AsyncSession
    ):

        result = await db.execute(
            select(Dataset)
        )

        return result.scalars().all()


dataset_repository = (
    DatasetRepository()
)