from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.dataset_records.models.dataset_record import (
    DatasetRecord
)


class DatasetRecordRepository:

    async def create(

        self,

        db: AsyncSession,

        dataset_record: DatasetRecord

    ):

        db.add(dataset_record)

        await db.flush()

        await db.refresh(
            dataset_record
        )

        return dataset_record

    async def get_by_id(

        self,

        db: AsyncSession,

        dataset_record_id: int

    ):

        result = await db.execute(

            select(
                DatasetRecord
            )
            .where(
                DatasetRecord.id
                ==
                dataset_record_id
            )
        )

        return result.scalar_one_or_none()
    
    async def get_by_dataset_and_hash(

        self,

        db: AsyncSession,

        dataset_id: int,

        record_hash: str

    ):

        result = await db.execute(

            select(
                DatasetRecord
            )
            .where(
                DatasetRecord.dataset_id
                == dataset_id,

                DatasetRecord.record_hash
                == record_hash
            )
        )

        return result.scalar_one_or_none()

    async def list_by_dataset(

        self,

        db: AsyncSession,

        dataset_id: int

    ):

        result = await db.execute(

            select(
                DatasetRecord
            )
            .where(
                DatasetRecord.dataset_id
                ==
                dataset_id
            )
        )

        return result.scalars().all()


dataset_record_repository = (
    DatasetRecordRepository()
)