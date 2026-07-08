from collections.abc import (
    AsyncIterator,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.dataset_records.repositories.dataset_record_repository import (
    dataset_record_repository,
)

from app.modules.training_runtime.contracts.training_data_stream import (
    TrainingDataStream,
)

from app.modules.training_runtime.schemas.training_data_batch import (
    TrainingDataBatch,
)

from app.modules.training_runtime.schemas.training_data_record import (
    TrainingDataRecord,
)


class DatasetSnapshotTrainingDataStream(
    TrainingDataStream
):

    def __init__(
        self,
        db: AsyncSession,
        dataset_id: int,
        max_record_id: int | None,
        batch_size: int,
    ):

        if batch_size <= 0:
            raise ValueError(
                "batch_size must be greater than zero."
            )

        self._db = db

        self._dataset_id = dataset_id

        self._max_record_id = (
            max_record_id
        )

        self._batch_size = batch_size


    async def iter_batches(
        self,
    ) -> AsyncIterator[
        TrainingDataBatch
    ]:

        last_seen_id: int | None = None

        while True:

            records = await (
                dataset_record_repository
                .list_snapshot_batch(
                    db=self._db,
                    dataset_id=self._dataset_id,
                    max_record_id=(
                        self._max_record_id
                    ),
                    batch_size=(
                        self._batch_size
                    ),
                    last_seen_id=(
                        last_seen_id
                    ),
                )
            )

            if not records:
                break

            batch_records = [

                TrainingDataRecord(
                    record_id=record.id,
                    dataset_id=record.dataset_id,
                    record_type=record.record_type,
                    input_text=record.input_text,
                    output_text=record.output_text,
                    metadata=(
                        record.metadata_json
                        or
                        {}
                    ),
                )

                for record in records
            ]

            yield TrainingDataBatch(
                records=batch_records,
                first_record_id=records[0].id,
                last_record_id=records[-1].id,
                record_count=len(records),
            )

            last_seen_id = (
                records[-1].id
            )