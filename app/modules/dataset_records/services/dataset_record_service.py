import hashlib

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.dataset_records.models.dataset_record import (
    DatasetRecord
)

from app.modules.dataset_records.schemas.dataset_record_create import (
    DatasetRecordCreate
)

from app.modules.dataset_records.schemas.dataset_record_list_response import (
    DatasetRecordListResponse,
)

from app.modules.dataset_records.repositories.dataset_record_repository import (
    dataset_record_repository
)

from app.modules.datasets.repositories.dataset_repository import (
    dataset_repository
)

from app.modules.corpora.repositories.corpus_source_repository import (
    corpus_source_repository
)


class DatasetRecordService:

    async def create_dataset_record(

        self,

        db: AsyncSession,

        data: DatasetRecordCreate

    ):

        dataset = await (
            dataset_repository
            .get_by_id_for_update(
                db,
                data.dataset_id,
            )
        )

        if not dataset:

            raise ValueError(
                "Dataset not found"
            )

        if data.corpus_source_id is not None:

            corpus_source = await (

                corpus_source_repository
                .get_by_id(
                    db,
                    data.corpus_source_id
                )
            )

            if not corpus_source:

                raise ValueError(
                    "Corpus source not found"
                )

        record_hash = hashlib.sha256(

            (
                data.input_text +
                (data.output_text or "")
            ).encode("utf-8")

        ).hexdigest()

        existing = await (

            dataset_record_repository
            .get_by_dataset_and_hash(
                db,
                data.dataset_id,
                record_hash
            )
        )

        if existing:

            raise ValueError(
                "Dataset record already exists"
            )

        dataset_record = DatasetRecord(
 
            dataset_id=data.dataset_id,

            corpus_source_id=data.corpus_source_id,

            record_type=data.record_type,

            status=data.status,

            record_hash=record_hash,

            validation_score=None,

            input_text=data.input_text,

            output_text=data.output_text,

            metadata_json=data.metadata_json
        )

        return await (

            dataset_record_repository
            .create(
                db,
                dataset_record
            )
        )

    async def get_dataset_record(

        self,

        db: AsyncSession,

        dataset_record_id: int

    ):

        return await (
            dataset_record_repository
            .get_by_id(
                db,
                dataset_record_id
            )
        )

    async def list_dataset_records(

        self,

        db: AsyncSession,

        dataset_id: int,

        page: int,

        page_size: int,

        search: str | None,

        status: str | None,

    ):

        items, total = await (

            dataset_record_repository
            .list_dataset_records(

                db=db,

                dataset_id=dataset_id,

                page=page,

                page_size=page_size,

                search=search,

                status=status,

            )

        )

        return DatasetRecordListResponse(

            items=items,

            total=total,

            page=page,

            page_size=page_size,

            total_pages=(

                (total + page_size - 1)

                //

                page_size

            ),

        )


dataset_record_service = (
    DatasetRecordService()
)