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

from app.modules.datasets.schemas.dataset_update import (
    DatasetUpdate,
)

from app.modules.datasets.schemas.dataset_list_response import (
    DatasetListResponse,
)


class DatasetService:

    async def create_dataset(
        self,
        db: AsyncSession,
        data: DatasetCreate
    ):

        dataset = Dataset(

            corpus_id=data.corpus_id,

            name=data.name,

            domain=data.domain,

            version=data.version,

            description=data.description,

            source=data.source,

            record_count=0,

            status="CREATED",

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

    
    async def list_datasets(

        self,

        db: AsyncSession,

        page: int,

        page_size: int,

        search: str | None,

        domain: str | None,

        status: str | None,

        sort: str,

        direction: str,

    ):

        items, total = await (

            dataset_repository.list(

                db=db,

                page=page,

                page_size=page_size,

                search=search,

                domain=domain,

                status=status,

                sort=sort,

                direction=direction,

            )

        )

        total_pages = (

            total + page_size - 1

        ) // page_size

        return DatasetListResponse(

            items=items,

            total=total,

            page=page,

            page_size=page_size,

            total_pages=total_pages,

        )

    async def update_dataset(
        self,
        db: AsyncSession,
        dataset_id: int,
        data: DatasetUpdate,
    ):

        dataset = await (
            dataset_repository
            .get_by_id_for_update(
                db,
                dataset_id,
            )
        )

        if dataset is None:

            raise ValueError(
                "Dataset not found."
            )

        values = (
            data.model_dump(
                exclude_unset=True
            )
        )

        for key, value in values.items():

            setattr(
                dataset,
                key,
                value,
            )

        return await (
            dataset_repository
            .update(
                db,
                dataset,
            )
        )

    async def delete_dataset(
        self,
        db: AsyncSession,
        dataset_id: int,
    ):

        dataset = await (
            dataset_repository
            .get_by_id_for_update(
                db,
                dataset_id,
            )
        )

        if dataset is None:

            raise ValueError(
                "Dataset not found."
            )

        await (
            dataset_repository
            .delete(
                db,
                dataset,
            )
        )


dataset_service = (
    DatasetService()
)