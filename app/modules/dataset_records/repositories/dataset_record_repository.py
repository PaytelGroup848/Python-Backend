from sqlalchemy import (
    func,
    select,
)

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

    async def list_dataset_records(

        self,

        db: AsyncSession,

        dataset_id: int,

        page: int,

        page_size: int,

        search: str | None,

        status: str | None,

    ):

        query = (

            select(

                DatasetRecord

            )

            .where(

                DatasetRecord.dataset_id

                ==

                dataset_id

            )

        )

        if search:

            search_text = f"%{search}%"

            query = query.where(

                DatasetRecord.input_text.ilike(search_text)

                |

                DatasetRecord.output_text.ilike(search_text)

            )

        if status:

            query = query.where(

                DatasetRecord.status

                ==

                status

            )

        count_query = (

            select(

                func.count()

            )

            .select_from(

                query.subquery()

            )

        )

        total_result = await db.execute(

            count_query

        )

        total = int(

            total_result.scalar_one()

        )

        result = await db.execute(

            query

            .order_by(

                DatasetRecord.id.desc()

            )

            .offset(

                (page - 1)

                *

                page_size

            )

            .limit(

                page_size

            )

        )

        return (

            result.scalars().all(),

            total,

        )
    

    async def list_batch_by_dataset(
        self,
        db: AsyncSession,
        dataset_id: int,
        batch_size: int,
        last_seen_id: int | None = None
    ):

        if batch_size <= 0:

            raise ValueError(
                "batch_size must be greater than zero."
            )

        query = (
            select(
                DatasetRecord
            )
            .where(
                DatasetRecord.dataset_id
                ==
                dataset_id
            )
        )

        if last_seen_id is not None:
 
            query = query.where(
                DatasetRecord.id
                >
                last_seen_id
            )

        query = (
            query
            .order_by(
                DatasetRecord.id.asc()
            )
            .limit(
                batch_size
            )
        )

        result = await db.execute(
            query
        )

        return result.scalars().all()
    
    async def get_max_id_by_dataset(
        self,
        db: AsyncSession,
        dataset_id: int,
    ) -> int | None:

        result = await db.execute(
            select(
                func.max(
                    DatasetRecord.id
                )
            )
            .where(
                DatasetRecord.dataset_id
                ==
                dataset_id
            )
        )

        return result.scalar_one_or_none()


    async def count_by_dataset_up_to_id(
        self,
        db: AsyncSession,
        dataset_id: int,
        max_record_id: int | None,
    ) -> int:

        if max_record_id is None:

            return 0

        result = await db.execute(
            select(
                func.count(
                    DatasetRecord.id
                )
            )
            .where(
                DatasetRecord.dataset_id
                ==
                dataset_id,

                DatasetRecord.id
                <=
                max_record_id,
            )
        )

        return int(
            result.scalar_one()
        )


    async def list_snapshot_batch(
        self,
        db: AsyncSession,
        dataset_id: int,
        max_record_id: int | None,
        batch_size: int,
        last_seen_id: int | None = None,
    ):

        if batch_size <= 0:

            raise ValueError(
                "batch_size must be greater than zero."
            )

        if max_record_id is None:

            return []

        query = (
            select(
                DatasetRecord
            )
            .where(
                DatasetRecord.dataset_id
                ==
                dataset_id,

                DatasetRecord.id
                <=
                max_record_id,
            )
        )

        if last_seen_id is not None:

            query = query.where(
                DatasetRecord.id
                >
                last_seen_id
            )

        query = (
            query
            .order_by(
                DatasetRecord.id.asc()
            )
            .limit(
                batch_size
            )
        )

        result = await db.execute(
            query
        )

        return result.scalars().all()
    



dataset_record_repository = (
    DatasetRecordRepository()
)