from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.training_runtime.providers.runtime_factory import (
    training_runtime_factory,
)

from app.modules.training_runtime.services.training_data_runtime_service import (
    training_data_runtime_service,
)

from app.modules.training_runtime.services.training_runtime_service import (
    training_runtime_service,
)

from app.modules.training_runtime.services.training_tokenization_service import (
    training_tokenization_service,
)

from app.modules.model_artifacts.repositories.model_artifact_repository import (
    model_artifact_repository,
)

from app.modules.training_runtime.schemas.training_execution_context import (
    TrainingExecutionContext,
)

from app.modules.training_runtime.schemas.training_result_schema import (
    TrainingResult,
)


class TrainingExecutorService:

    async def execute(
        self,
        db: AsyncSession,
        training_job_id: int,
    ) -> TrainingResult:

        print("[EXECUTOR] 1 BEFORE load_runtime", flush=True)

        runtime = await (
            training_runtime_service
            .load_runtime(
                db=db,
                training_job_id=training_job_id,
            )
        )

        print("[EXECUTOR] 2 AFTER load_runtime", flush=True)

        tokenizer_configuration = (
            runtime.runtime_configuration.get(
                "tokenizer"
            )
        )

        if not isinstance(
            tokenizer_configuration,
            dict,
        ):
            raise ValueError(
                "Training configuration must define "
                "'tokenizer' as an object."
            )

        print("[EXECUTOR] 3 BEFORE prepare_configuration", flush=True)

        prepared_tokenizer_configuration = await (
            training_tokenization_service
            .prepare_configuration(
                db=db,
                tokenizer_version_id=(
                    runtime.tokenizer_version_id
                ),
                tokenizer_configuration=(
                    tokenizer_configuration
                ),
            )
        )

        print("[EXECUTOR] 4 AFTER prepare_configuration", flush=True)

        prepared_runtime_configuration = dict(
            runtime.runtime_configuration
        )

        prepared_runtime_configuration[
            "tokenizer"
        ] = prepared_tokenizer_configuration


        runtime = runtime.model_copy(
            update={
                "runtime_configuration": (
                    prepared_runtime_configuration
                )
            }
        )

        training_configuration = (
            runtime.runtime_configuration.get(
                "training"
            )
        )

        if not isinstance(
            training_configuration,
            dict,
        ):
            raise ValueError(
                "Training configuration must define "
                "'training' as an object."
            )

        batch_size = (
            training_configuration.get(
                "data_batch_size"
            )
        )

        if batch_size is None:
            raise ValueError(
                "Training configuration.training "
                "must define 'data_batch_size'."
            )

        if (
            isinstance(batch_size, bool)
            or
            not isinstance(batch_size, int)
            or
            batch_size <= 0
        ):
            raise ValueError(
                "'training.data_batch_size' "
                "must be a positive integer."
            )
        
        resume_after_record_id = None

        checkpoint_configuration = (
            runtime.runtime_configuration
            .get(
                "checkpoint"
            )
        )

        if checkpoint_configuration is not None:

            if not isinstance(
                checkpoint_configuration,
                dict,
            ):
                raise ValueError(
                    "'checkpoint' must be an object."
                )

            resume_enabled = (
                checkpoint_configuration.get(
                    "resume_enabled",
                    False,
                )
            )

            if not isinstance(
                resume_enabled,
                bool,
            ):
                raise ValueError(
                    "'resume_enabled' must be boolean."
                )

            if resume_enabled:

                checkpoint_artifact = await (
                    model_artifact_repository
                    .get_latest_by_type(
                        db=db,
                        training_job_id=(
                            runtime.training_job_id
                        ),
                        artifact_type=(
                            "TRAINING_CHECKPOINT"
                        ),
                    )
                )

                if checkpoint_artifact is not None:

                    metadata = (
                        checkpoint_artifact
                        .metadata_json
                        or
                        {}
                    )

                    if not isinstance(
                        metadata,
                        dict,
                    ):
                        raise ValueError(
                            "Checkpoint metadata "
                            "is invalid."
                        )

                    data_cursor = (
                        metadata.get(
                            "data_cursor",
                            {},
                        )
                    )

                    if not isinstance(
                        data_cursor,
                        dict,
                    ):
                        raise ValueError(
                            "Checkpoint data cursor "
                            "is invalid."
                        )

                    resume_after_record_id = (
                        data_cursor.get(
                            "last_record_id"
                        )
                    )

                    if (
                        resume_after_record_id
                        is not None
                        and
                        (
                            isinstance(
                                resume_after_record_id,
                                bool,
                            )
                            or
                            not isinstance(
                                resume_after_record_id,
                                int,
                            )
                            or
                            resume_after_record_id
                            <
                            0
                        )
                    ):
                        raise ValueError(
                            "Checkpoint resume cursor "
                            "is invalid."
                        )

        print("[EXECUTOR] 5 BEFORE open_snapshot_stream", flush=True)

        training_data = await (
            training_data_runtime_service
            .open_snapshot_stream(
                db=db,
                dataset_snapshot_id=(
                    runtime.dataset_snapshot_id
                ),
                batch_size=batch_size,
                resume_after_record_id=(
                    resume_after_record_id
                ),
            )
        )

        print("[EXECUTOR] 6 AFTER open_snapshot_stream", flush=True)

        print("[EXECUTOR] 7 BEFORE get_runtime", flush=True)



        training_runtime = (
            training_runtime_factory
            .get_runtime(
                runtime.runtime_class
            )
        )

        print("[EXECUTOR] 8 AFTER get_runtime", flush=True)



        if training_runtime is None:

            raise ValueError(
                f"No runtime registered for "
                f"{runtime.runtime_class}."
            )
        #execution_context = (
         #   TrainingExecutionContext(
          #      db=db,
           # )
        #)

        #print("[EXECUTOR] runtime object:", training_runtime, flush=True)
        #print("[EXECUTOR] runtime type:", type(training_runtime), flush=True)

        #return await (
         #   training_runtime.execute(
          #      runtime=runtime,
           #     training_data=training_data,
            #    context=execution_context,
            #)
        #
        #print("[EXECUTOR] runtime.execute() returned", flush=True)

        #return result

    

        #print("[EXECUTOR] 9 BEFORE runtime.execute()", flush=True)

        execution_context = TrainingExecutionContext(
            db=db,
        )

        print("[EXECUTOR] runtime object:", training_runtime, flush=True)
        print("[EXECUTOR] runtime type:", type(training_runtime), flush=True)

        result = await training_runtime.execute(
            runtime=runtime,
            training_data=training_data,
            context=execution_context,
        )

        print("[EXECUTOR] runtime.execute() returned", flush=True)

        return result
    


training_executor_service = (
    TrainingExecutorService()
)