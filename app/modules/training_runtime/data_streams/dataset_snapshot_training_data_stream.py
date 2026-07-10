import asyncio

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
        dataset_snapshot_id: int,
        dataset_id: int,
        max_record_id: int | None,
        batch_size: int,
        resume_after_record_id: int | None = None,
    ):

        if dataset_snapshot_id <= 0:
            raise ValueError(
                "dataset_snapshot_id must be greater than zero."
            )

        if dataset_id <= 0:
            raise ValueError(
                "dataset_id must be greater than zero."
            )

        if batch_size <= 0:
            raise ValueError(
                "batch_size must be greater than zero."
            )

        if (
            max_record_id is not None
            and
            max_record_id <= 0
        ):
            raise ValueError(
                "max_record_id must be greater than zero "
                "when provided."
            )

        if (
            resume_after_record_id is not None
            and
            resume_after_record_id < 0
        ):
            raise ValueError(
                "resume_after_record_id cannot be negative."
            )

        if (
            max_record_id is not None
            and
            resume_after_record_id is not None
            and
            resume_after_record_id > max_record_id
        ):
            raise ValueError(
                "resume_after_record_id cannot exceed "
                "the snapshot max_record_id."
            )

        self._db = db

        self._dataset_snapshot_id = (
            dataset_snapshot_id
        )

        self._dataset_id = dataset_id

        self._max_record_id = (
            max_record_id
        )

        self._batch_size = batch_size

        self._resume_after_record_id = (
            resume_after_record_id
        )

        self._cancel_requested = False

        self._closed = False

        self._iteration_active = False

        self._state_lock = asyncio.Lock()


    @property
    def dataset_snapshot_id(
        self,
    ) -> int:

        return self._dataset_snapshot_id


    @property
    def resume_after_record_id(
        self,
    ) -> int | None:

        return self._resume_after_record_id


    def request_cancel(
        self,
    ) -> None:

        self._cancel_requested = True


    async def aclose(
        self,
    ) -> None:

        async with self._state_lock:

            self._closed = True

            self._cancel_requested = True


    async def iter_batches(
        self,
    ) -> AsyncIterator[
        TrainingDataBatch
    ]:

        async with self._state_lock:

            if self._closed:
                raise RuntimeError(
                    "Training data stream is closed."
                )

            if self._iteration_active:
                raise RuntimeError(
                    "Training data stream already has "
                    "an active consumer."
                )

            self._iteration_active = True

        last_seen_id = (
            self._resume_after_record_id
        )

        try:

            while True:

                if (
                    self._closed
                    or
                    self._cancel_requested
                ):
                    break

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

                if (
                    self._closed
                    or
                    self._cancel_requested
                ):
                    break

                if not records:
                    break

                previous_record_id = (
                    last_seen_id
                )

                for record in records:

                    if (
                        previous_record_id is not None
                        and
                        record.id <= previous_record_id
                    ):
                        raise RuntimeError(
                            "Dataset snapshot stream returned "
                            "non-monotonic record ordering."
                        )

                    if (
                        self._max_record_id is not None
                        and
                        record.id > self._max_record_id
                    ):
                        raise RuntimeError(
                            "Dataset snapshot stream returned "
                            "a record beyond max_record_id."
                        )

                    if (
                        record.dataset_id
                        !=
                        self._dataset_id
                    ):
                        raise RuntimeError(
                            "Dataset snapshot stream returned "
                            "a record from another dataset."
                        )

                    previous_record_id = (
                        record.id
                    )

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

                batch = TrainingDataBatch(
                    records=batch_records,
                    first_record_id=records[0].id,
                    last_record_id=records[-1].id,
                    record_count=len(records),
                )

                yield batch

                last_seen_id = (
                    batch.last_record_id
                )

        finally:

            async with self._state_lock:

                self._iteration_active = False