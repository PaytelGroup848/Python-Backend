from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.datasets.models.dataset import Dataset
from app.modules.corpora.models.corpus import Corpus
from app.modules.datasets.repositories.dataset_repository import dataset_repository
from app.modules.datasets.schemas.dataset_create import DatasetCreate
from app.modules.datasets.schemas.dataset_update import DatasetUpdate
from app.modules.datasets.schemas.dataset_list_response import DatasetListResponse


class DatasetService:

    async def create_dataset(
        self,
        db: AsyncSession,
        data: DatasetCreate
    ):
        # Verify corpus exists or create default
        corpus_id = data.corpus_id or 1
        res = await db.execute(select(Corpus).where(Corpus.id == corpus_id))
        corpus = res.scalars().first()

        if not corpus:
            corpus = Corpus(
                id=corpus_id,
                name=f"{data.domain.capitalize()} Corpus {corpus_id}",
                domain=data.domain or "general",
                description=f"Auto-generated corpus for domain {data.domain}",
                status="ACTIVE"
            )
            db.add(corpus)
            await db.flush()

        dataset = Dataset(
            corpus_id=corpus.id,
            name=data.name,
            domain=data.domain,
            version=data.version,
            description=data.description,
            source=data.source,
            record_count=0,
            status="CREATED",
        )

        return await dataset_repository.create(db, dataset)

    async def get_dataset(
        self,
        db: AsyncSession,
        dataset_id: int
    ):
        dataset = await dataset_repository.get_by_id(db, dataset_id)
        if not dataset:
            return None

        # Compute live statistics for dataset
        from sqlalchemy import text
        r_res = await db.execute(text("SELECT COUNT(*) FROM dataset_records WHERE dataset_id = :did"), {"did": dataset_id})
        s_res = await db.execute(text("SELECT COUNT(*) FROM dataset_snapshots WHERE dataset_id = :did"), {"did": dataset_id})

        rec_count = r_res.scalar() or 0
        snap_count = s_res.scalar() or 0

        # Update dataset model attribute dynamically
        dataset.record_count = rec_count
        setattr(dataset, "snapshot_count", snap_count)
        setattr(dataset, "training_job_count", 0)

        return dataset


    
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

        from sqlalchemy import text
        for item in items:
            r_res = await db.execute(text("SELECT COUNT(*) FROM dataset_records WHERE dataset_id = :did"), {"did": item.id})
            s_res = await db.execute(text("SELECT COUNT(*) FROM dataset_snapshots WHERE dataset_id = :did"), {"did": item.id})
            item.record_count = r_res.scalar() or 0
            setattr(item, "snapshot_count", s_res.scalar() or 0)
            setattr(item, "training_job_count", 0)

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