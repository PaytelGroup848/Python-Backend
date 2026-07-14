from sqlalchemy import (
    asc,
    desc,
    func,
    select,
)
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

    async def list(

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

        query = select(
            Dataset
        )

    #
    # Search
    #

        if search:

            query = query.where(

                Dataset.name.ilike(
                    f"%{search}%"
                )

            )

    #
    # Domain
    #

        if domain:

            query = query.where(

                Dataset.domain
                ==
                domain

            )

    #
    # Status
    #

        if status:

            query = query.where(

                Dataset.status
                ==
                status

            )

    #
    # Total Count
    #

        count_query = (

            select(

                func.count()

            )

            .select_from(

                query.subquery()

            )

        )

        total = (

            await db.execute(
                count_query
            )

        ).scalar_one()

    #
    # Sorting
    #

        sort_column = getattr(
 
            Dataset,

            sort,

            Dataset.created_at,

        )

        if direction == "asc":

            query = query.order_by(

                asc(
                    sort_column
                )

            )

        else:

            query = query.order_by(

                desc(
                    sort_column
                )

            )

    #
    # Pagination
    #

        query = (

            query

            .offset(

                (

                    page - 1

                )

                * page_size

            )

            .limit(

                page_size

            )

        )

        result = await db.execute(

            query

        )

        return (

            result.scalars().all(),

            total,

        )
    
    async def delete(
        self,
        db: AsyncSession,
        dataset: Dataset,
    ):

        await db.delete(
            dataset
        )

    async def get_by_corpus_and_version(
        self,
        db: AsyncSession,
        corpus_id: int,
        version: str,
    ):

        result = await db.execute(

            select(
                Dataset
            )
            .where(
                Dataset.corpus_id
                ==
                corpus_id
            )
            .where(
                Dataset.version
                ==
                version
            )

        )

        return result.scalar_one_or_none()

    async def get_by_name(
        self,
        db: AsyncSession,
        name: str,
    ):

        result = await db.execute(

            select(
                Dataset
            )
            .where(
                Dataset.name
                ==
                name
            )

        )

        return result.scalar_one_or_none()


dataset_repository = (
    DatasetRepository()
)