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
    ) -> TrainingDataStream:

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

        return DatasetSnapshotTrainingDataStream(
            db=db,
            dataset_id=snapshot.dataset_id,
            max_record_id=snapshot.max_record_id,
            batch_size=batch_size,
        )


training_data_runtime_service = (
    TrainingDataRuntimeService()
)