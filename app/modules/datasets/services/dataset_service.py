from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.datasets.models.dataset import (
    Dataset
)

from app.modules.datasets.repositories.dataset_repository import (
    dataset_repository
)

from app.modules.datasets.schemas.dataset_create import (
    DatasetCreate
)


class DatasetService:

    async def create_dataset(
        self,
        db: AsyncSession,
        data: DatasetCreate
    ):

        dataset = Dataset(
            **data.model_dump()
        )

        return await (
            dataset_repository
            .create(
                db,
                dataset
            )
        )

    async def get_dataset(
        self,
        db: AsyncSession,
        dataset_id: int
    ):

        return await (
            dataset_repository
            .get_by_id(
                db,
                dataset_id
            )
        )


dataset_service = (
    DatasetService()
)