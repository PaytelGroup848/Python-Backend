from sqlalchemy import (
    select,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.datasets.models.dataset_upload import (
    DatasetUpload,
)


class DatasetUploadRepository:

    async def create(

        self,

        db: AsyncSession,

        dataset_upload: DatasetUpload,

    ) -> DatasetUpload:

        db.add(
            dataset_upload
        )

        await db.flush()

        await db.refresh(
            dataset_upload
        )

        return dataset_upload

    async def update(

        self,

        db: AsyncSession,

        dataset_upload: DatasetUpload,

    ) -> DatasetUpload:

        await db.flush()

        await db.refresh(
            dataset_upload
        )

        return dataset_upload

    async def delete(

        self,

        db: AsyncSession,

        dataset_upload: DatasetUpload,

    ):

        await db.delete(
            dataset_upload
        )

    async def get_by_id(

        self,

        db: AsyncSession,

        upload_id: int,

    ) -> DatasetUpload | None:

        result = await db.execute(

            select(
                DatasetUpload
            ).where(
                DatasetUpload.id
                ==
                upload_id
            )

        )

        return result.scalar_one_or_none()

    async def get_by_stored_file_name(

        self,

        db: AsyncSession,

        stored_file_name: str,

    ) -> DatasetUpload | None:

        result = await db.execute(

            select(
                DatasetUpload
            ).where(
                DatasetUpload.stored_file_name
                ==
                stored_file_name
            )

        )

        return result.scalar_one_or_none()

    async def list_by_dataset(

        self,

        db: AsyncSession,

        dataset_id: int,

    ) -> list[DatasetUpload]:

        result = await db.execute(

            select(
                DatasetUpload
            )
            .where(
                DatasetUpload.dataset_id
                ==
                dataset_id
            )
            .where(
                DatasetUpload.is_deleted
                ==
                False
            )
            .order_by(
                DatasetUpload.created_at.desc()
            )

        )

        return result.scalars().all()

    async def list_pending_ingestion(

        self,

        db: AsyncSession,

    ) -> list[DatasetUpload]:

        result = await db.execute(

            select(
                DatasetUpload
            )
            .where(
                DatasetUpload.ingestion_status
                ==
                "PENDING"
            )
            .where(
                DatasetUpload.is_deleted
                ==
                False
            )
            .order_by(
                DatasetUpload.created_at.asc()
            )

        )

        return result.scalars().all()

    async def list_failed_ingestion(

        self,

        db: AsyncSession,

    ) -> list[DatasetUpload]:

        result = await db.execute(

            select(
                DatasetUpload
            )
            .where(
                DatasetUpload.ingestion_status
                ==
                "FAILED"
            )
            .where(
                DatasetUpload.is_deleted
                ==
                False
            )
            .order_by(
                DatasetUpload.created_at.desc()
            )

        )

        return result.scalars().all()

    async def mark_deleted(

        self,

        db: AsyncSession,

        dataset_upload: DatasetUpload,

    ) -> DatasetUpload:

        dataset_upload.is_deleted = True

        await db.flush()

        await db.refresh(
            dataset_upload
        )

        return dataset_upload


dataset_upload_repository = (
    DatasetUploadRepository()
)