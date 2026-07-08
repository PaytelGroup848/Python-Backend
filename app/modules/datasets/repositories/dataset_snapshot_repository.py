from sqlalchemy import (
    select,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.datasets.models.dataset_snapshot import (
    DatasetSnapshot,
)


class DatasetSnapshotRepository:

    async def create(
        self,
        db: AsyncSession,
        snapshot: DatasetSnapshot,
    ):

        db.add(
            snapshot
        )

        await db.flush()

        await db.refresh(
            snapshot
        )

        return snapshot


    async def get_by_id(
        self,
        db: AsyncSession,
        snapshot_id: int,
    ):

        result = await db.execute(
            select(
                DatasetSnapshot
            )
            .where(
                DatasetSnapshot.id
                ==
                snapshot_id
            )
        )

        return result.scalar_one_or_none()


    async def get_by_dataset_and_code(
        self,
        db: AsyncSession,
        dataset_id: int,
        snapshot_code: str,
    ):

        result = await db.execute(
            select(
                DatasetSnapshot
            )
            .where(
                DatasetSnapshot.dataset_id
                ==
                dataset_id,

                DatasetSnapshot.snapshot_code
                ==
                snapshot_code,
            )
        )

        return result.scalar_one_or_none()


    async def list_by_dataset(
        self,
        db: AsyncSession,
        dataset_id: int,
    ):

        result = await db.execute(
            select(
                DatasetSnapshot
            )
            .where(
                DatasetSnapshot.dataset_id
                ==
                dataset_id
            )
            .order_by(
                DatasetSnapshot.id.desc()
            )
        )

        return result.scalars().all()
    
    async def get_by_id_for_update(
        self,
        db: AsyncSession,
        snapshot_id: int,
    ):

        result = await db.execute(
            select(
                DatasetSnapshot
            )
            .where(
                DatasetSnapshot.id
                ==
                snapshot_id
            )
            .with_for_update()
        )

        return result.scalar_one_or_none()


dataset_snapshot_repository = (
    DatasetSnapshotRepository()
)