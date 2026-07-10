from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.datasets.repositories.dataset_snapshot_repository import (
    dataset_snapshot_repository,
)

from app.modules.training_runtime.contracts.training_data_stream import (
    TrainingDataStream,
)

from app.modules.training_runtime.data_streams.dataset_snapshot_training_data_stream import (
    DatasetSnapshotTrainingDataStream,
)


class TrainingDataRuntimeService:

    async def open_snapshot_stream(
        self,
        db: AsyncSession,
        dataset_snapshot_id: int,
        batch_size: int,
        resume_after_record_id: int | None = None,
    ) -> TrainingDataStream:

        if dataset_snapshot_id <= 0:
            raise ValueError(
                "dataset_snapshot_id must be greater than zero."
            )

        if batch_size <= 0:
            raise ValueError(
                "batch_size must be greater than zero."
            )

        if (
            resume_after_record_id is not None
            and
            resume_after_record_id < 0
        ):
            raise ValueError(
                "resume_after_record_id cannot be negative."
            )

        snapshot = await (
            dataset_snapshot_repository
            .get_by_id(
                db=db,
                snapshot_id=dataset_snapshot_id,
            )
        )

        if snapshot is None:
            raise ValueError(
                "Dataset snapshot not found."
            )

        if snapshot.status.upper() != "SEALED":
            raise ValueError(
                "Training requires a SEALED dataset snapshot."
            )

        if not snapshot.is_immutable:
            raise ValueError(
                "Training requires an immutable dataset snapshot."
            )

        if snapshot.record_count < 0:
            raise ValueError(
                "Dataset snapshot record_count cannot be negative."
            )

        if (
            snapshot.record_count > 0
            and
            snapshot.max_record_id is None
        ):
            raise ValueError(
                "Non-empty dataset snapshot must define "
                "max_record_id."
            )

        if (
            snapshot.max_record_id is not None
            and
            snapshot.max_record_id <= 0
        ):
            raise ValueError(
                "Dataset snapshot max_record_id must be "
                "greater than zero when provided."
            )

        if (
            resume_after_record_id is not None
            and
            snapshot.max_record_id is None
        ):
            raise ValueError(
                "Cannot resume a snapshot without "
                "max_record_id."
            )

        if (
            resume_after_record_id is not None
            and
            snapshot.max_record_id is not None
            and
            resume_after_record_id
            >
            snapshot.max_record_id
        ):
            raise ValueError(
                "resume_after_record_id cannot exceed "
                "the snapshot max_record_id."
            )

        return DatasetSnapshotTrainingDataStream(
            db=db,
            dataset_snapshot_id=snapshot.id,
            dataset_id=snapshot.dataset_id,
            max_record_id=snapshot.max_record_id,
            batch_size=batch_size,
            resume_after_record_id=(
                resume_after_record_id
            ),
        )


training_data_runtime_service = (
    TrainingDataRuntimeService()
)