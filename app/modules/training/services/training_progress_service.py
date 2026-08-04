from datetime import datetime

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.training.repositories.training_job_repository import (
    training_job_repository,
)

from app.modules.training_runtime.schemas.training_execution_context import (
    TrainingExecutionContext,
)

from app.modules.training_runtime.contracts.training_progress_reporter import (
    TrainingProgressReporter,
)

from app.modules.training_runtime.schemas.training_runtime_schema import (
    TrainingRuntime,
)


class TrainingProgressService(
    TrainingProgressReporter
):

    async def on_training_started(
        self,
        runtime: TrainingRuntime,
        context: TrainingExecutionContext,
    ) -> None:

        await self._persist_progress(
            db=context.db,
            training_job_id=runtime.training_job_id,
        )


    async def on_epoch_started(
        self,
        runtime: TrainingRuntime,
        context: TrainingExecutionContext,
        epoch: int,
    ) -> None:

        await self._persist_progress(
            db=context.db,
            training_job_id=runtime.training_job_id,
            current_epoch=epoch,
        )


    async def on_batch_completed(
        self,
        runtime: TrainingRuntime,
        context: TrainingExecutionContext,
        epoch: int,
        step: int,
        global_step: int,
        current_loss: float | None,
        learning_rate: float | None,
        processed_samples: int,
        processed_tokens: int,
    ) -> None:

        await self._persist_progress(

            db=context.db,

            training_job_id=runtime.training_job_id,

            current_epoch=epoch,

            current_step=step,

            global_step=global_step,

            current_loss=current_loss,

            learning_rate=learning_rate,

            processed_samples=processed_samples,

            processed_tokens=processed_tokens,
        )


    async def on_checkpoint_saved(
        self,
        runtime: TrainingRuntime,
        context: TrainingExecutionContext,
        checkpoint_path: str,
    ) -> None:

        await self._persist_progress(

            db=context.db,

            training_job_id=runtime.training_job_id,

            last_checkpoint_path=checkpoint_path,

        )


    async def on_training_completed(
        self,
        runtime: TrainingRuntime,
        context: TrainingExecutionContext,
    ) -> None:

        await self._persist_progress(

            db=context.db,

            training_job_id=runtime.training_job_id,

        )


    async def on_training_failed(
        self,
        runtime: TrainingRuntime,
        context: TrainingExecutionContext,
        failure_reason: str,
    ) -> None:

        await self._persist_progress(

            db=context.db,

            training_job_id=runtime.training_job_id,


            failure_reason=failure_reason,
        )


    async def _persist_progress(
        self,
        db: AsyncSession,
        training_job_id: int,
        **progress,
    ) -> None:

        training_job = await (
            training_job_repository
            .get_by_id(
                db=db,
                training_job_id=training_job_id,
            )
        )

        if training_job is None:

            raise ValueError(
                f"Training job {training_job_id} not found."
            )

        for field, value in progress.items():
 
            if hasattr(
                training_job,
                field,
            ):

                setattr(
                    training_job,
                    field,
                    value,
                )

        if (
            "last_checkpoint_path"
            in
            progress
        ):

            training_job.last_checkpoint_at = (
                datetime.utcnow()
            )

        await (
            training_job_repository
            .update(
                db=db,
                training_job=training_job,
            )
        )


training_progress_service = (
    TrainingProgressService()
)