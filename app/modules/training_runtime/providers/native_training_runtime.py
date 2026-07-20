from app.modules.training_runtime.contracts.training_data_stream import (
    TrainingDataStream,
)

from app.modules.training_runtime.contracts.trainable_model import (
    TrainableModel,
)

from app.modules.training_runtime.providers.base_training_runtime import (
    BaseTrainingRuntime,
)

from app.modules.training_runtime.schemas.training_runtime_schema import (
    TrainingRuntime,
)

from app.modules.training_runtime.schemas.training_result_schema import (
    TrainingResult,
)

from app.modules.training_runtime.services.training_model_initialization_service import (
    training_model_initialization_service,
)

from app.modules.training_runtime.services.training_sample_formatter_service import (
    training_sample_formatter_service,
)

from app.modules.training_runtime.services.training_strategy_service import (
    training_strategy_service,
)

from app.modules.training_runtime.services.training_tokenization_service import (
    training_tokenization_service,
)

from app.modules.training_runtime.schemas.training_execution_context import (
    TrainingExecutionContext,
)

from app.modules.training_runtime.services.training_final_artifact_service import (
    training_final_artifact_service,
)

from app.modules.training_runtime.services.training_checkpoint_service import (
    training_checkpoint_service,
)

from app.modules.training.services.training_progress_service import (
    training_progress_service,
)


class NativeTrainingRuntime(
    BaseTrainingRuntime
):

    async def execute(
        self,
        runtime: TrainingRuntime,
        training_data: TrainingDataStream,
        context: TrainingExecutionContext,
    ) -> TrainingResult:

        formatter_configuration = (
            runtime.runtime_configuration.get(
                "formatter"
            )
        )

        if not isinstance(
            formatter_configuration,
            dict,
        ):
            raise ValueError(
                "Training configuration must define "
                "'formatter' as an object."
            )

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

        checkpoint_configuration = (
            runtime.runtime_configuration.get(
                "checkpoint"
            )
        )

        if checkpoint_configuration is None:
            checkpoint_configuration = {}

        if not isinstance(
            checkpoint_configuration,
            dict,
        ):
            raise ValueError(
                "'checkpoint' must be an object."
            )

        checkpoint_enabled = (
            checkpoint_configuration.get(
                "enabled",
                False,
            )
        )

        resume_enabled = (
            checkpoint_configuration.get(
                "resume_enabled",
                False,
            )
        )

        if not isinstance(
            checkpoint_enabled,
            bool,
        ):
            raise ValueError(
                "'checkpoint.enabled' must be boolean."
            )

        if not isinstance(
            resume_enabled,
            bool,
        ):
            raise ValueError(
                "'checkpoint.resume_enabled' "
                "must be boolean."
            )

        checkpoint_every_steps = None

        if checkpoint_enabled:

            checkpoint_every_steps = (
                checkpoint_configuration.get(
                    "every_optimizer_steps"
                )
            )

            if (
                isinstance(
                    checkpoint_every_steps,
                    bool,
                )
                or
                not isinstance(
                    checkpoint_every_steps,
                    int,
                )
                or
                checkpoint_every_steps <= 0
            ):
                raise ValueError(
                    "'checkpoint.every_optimizer_steps' "
                    "must be a positive integer."
                )

        model = await (
            training_model_initialization_service
            .initialize(
                runtime=runtime,
            )
        )

        if not isinstance(
            model,
            TrainableModel,
        ):
            raise ValueError(
                "Model initialization did not return "
                "a TrainableModel instance."
            )

        (
            training_strategy,
            strategy_state,
            strategy_configuration,
        ) = await (
            training_strategy_service
            .initialize(
                runtime=runtime,
                model=model,
            )
        )

        await (
            training_progress_service
            .on_training_started(
                runtime=runtime,
                context=context,
            )
        )

        await context.db.commit()

        processed_record_count = 0
        processed_batch_count = 0
        formatted_sample_count = 0
        tokenized_sample_count = 0
        processed_token_count = 0
        trained_sample_count = 0

        loss_total = 0.0
        loss_observation_count = 0

        optimizer_step_count = 0
        micro_step_count = 0

        first_record_id: int | None = None
        last_record_id: int | None = None

        restored_checkpoint = None

        if resume_enabled:

            restored_checkpoint = await (
                training_checkpoint_service
                .restore_latest(
                    db=context.db,
                    runtime=runtime,
                    model=model,
                    strategy_state=(
                        strategy_state
                    ),
                    organization_id=(
                        context.organization_id
                    ),
                    workspace_id=(
                        context.workspace_id
                    ),
                )
            )

        if restored_checkpoint is not None:

            restored_data_cursor = (
                restored_checkpoint.get(
                    "data_cursor",
                    {},
                )
            )

            if not isinstance(
                restored_data_cursor,
                dict,
            ):
                raise ValueError(
                    "Restored checkpoint data cursor "
                    "is invalid."
                )

            restored_last_record_id = (
                restored_data_cursor.get(
                    "last_record_id"
                )
            )

            restored_processed_record_count = (
                restored_data_cursor.get(
                    "processed_record_count",
                    0,
                )
            )

            restored_processed_batch_count = (
                restored_data_cursor.get(
                    "processed_batch_count",
                    0,
                )
            )

            if (
                restored_last_record_id is not None
                and
                (
                    isinstance(
                        restored_last_record_id,
                        bool,
                    )
                    or
                    not isinstance(
                        restored_last_record_id,
                        int,
                    )
                    or
                    restored_last_record_id < 0
                )
            ):
                raise ValueError(
                    "Restored last record ID "
                    "is invalid."
                )

            if (
                isinstance(
                    restored_processed_record_count,
                    bool,
                )
                or
                not isinstance(
                    restored_processed_record_count,
                    int,
                )
                or
                restored_processed_record_count < 0
            ):
                raise ValueError(
                    "Restored processed record count "
                    "is invalid."
                )

            if (
                isinstance(
                    restored_processed_batch_count,
                    bool,
                )
                or
                not isinstance(
                    restored_processed_batch_count,
                    int,
                )
                or
                restored_processed_batch_count < 0
            ):
                raise ValueError(
                    "Restored processed batch count "
                    "is invalid."
                )

            last_record_id = (
                restored_last_record_id
            )

            processed_record_count = (
                restored_processed_record_count
            )

            processed_batch_count = (
                restored_processed_batch_count
            )

            formatted_sample_count = (
                restored_processed_record_count
            )

            tokenized_sample_count = (
                restored_processed_record_count
            )

            optimizer_step_count = int(
                restored_checkpoint.get(
                    "step_count",
                    strategy_state.get(
                        "step_count",
                        0,
                    ),
                )
            )

            micro_step_count = int(
                restored_checkpoint.get(
                    "micro_step_count",
                    strategy_state.get(
                        "micro_step_count",
                        0,
                    ),
                )
            )

            await (
                training_progress_service
                .on_batch_completed(
                    runtime=runtime,
                    context=context,
                    epoch=0,
                    step=optimizer_step_count,
                    global_step=optimizer_step_count,
                    current_loss=None,
                    learning_rate=None,
                    processed_samples=processed_record_count,
                    processed_tokens=processed_token_count,
                )
            )

            await context.db.commit()

        last_published_checkpoint_step = None

        async for batch in (
            training_data.iter_batches()
        ):

            formatted_samples = (
                training_sample_formatter_service
                .format_batch(
                    batch=batch,
                    formatter_configuration=(
                        formatter_configuration
                    ),
                )
            )

            tokenized_samples = (
                training_tokenization_service
                .tokenize_batch(
                    samples=formatted_samples,
                    tokenizer_configuration=(
                        tokenizer_configuration
                    ),
                )
            )

            batch_training_metrics = await (
                training_strategy
                .train_batch(
                    runtime=runtime,
                    model=model,
                    strategy_state=(
                        strategy_state
                    ),
                    samples=tokenized_samples,
                    configuration=(
                        strategy_configuration
                    ),
                )
            )

            if not isinstance(
                batch_training_metrics,
                dict,
            ):
                raise ValueError(
                    "Training strategy train_batch "
                    "must return an object."
                )

            batch_loss = (
                batch_training_metrics.get(
                    "loss"
                )
            )

            if (
                isinstance(batch_loss, bool)
                or
                not isinstance(
                    batch_loss,
                    (int, float),
                )
            ):
                raise ValueError(
                    "Training strategy returned "
                    "an invalid loss."
                )

            batch_trained_sample_count = (
                batch_training_metrics.get(
                    "sample_count"
                )
            )

            if (
                isinstance(
                    batch_trained_sample_count,
                    bool,
                )
                or
                not isinstance(
                    batch_trained_sample_count,
                    int,
                )
                or
                batch_trained_sample_count < 0
            ):
                raise ValueError(
                    "Training strategy returned "
                    "an invalid sample count."
                )

            returned_step_count = (
                batch_training_metrics.get(
                    "step_count"
                )
            )

            returned_micro_step_count = (
                batch_training_metrics.get(
                    "micro_step_count"
                )
            )

            if (
                isinstance(returned_step_count, bool)
                or
                not isinstance(
                    returned_step_count,
                    int,
                )
                or
                returned_step_count < 0
            ):
                raise ValueError(
                    "Training strategy returned "
                    "an invalid optimizer step count."
                )

            if (
                isinstance(
                    returned_micro_step_count,
                    bool,
                )
                or
                not isinstance(
                    returned_micro_step_count,
                    int,
                )
                or
                returned_micro_step_count < 0
            ):
                raise ValueError(
                    "Training strategy returned "
                    "an invalid micro step count."
                )

            previous_optimizer_step_count = (
                optimizer_step_count
            )

            optimizer_step_count = (
                returned_step_count
            )

            micro_step_count = (
                returned_micro_step_count
            )

            optimizer_step_performed = (
                optimizer_step_count
                >
                previous_optimizer_step_count
            )

            explicit_optimizer_step_performed = (
                batch_training_metrics.get(
                    "optimizer_step_performed"
                )
            )

            if (
                explicit_optimizer_step_performed
                is not None
            ):

                if not isinstance(
                    explicit_optimizer_step_performed,
                    bool,
                ):
                    raise ValueError(
                        "Training strategy returned "
                        "an invalid optimizer-step flag."
                    )

                optimizer_step_performed = (
                    explicit_optimizer_step_performed
                )

            loss_total += float(
                batch_loss
            )

            loss_observation_count += 1

            trained_sample_count += (
                batch_trained_sample_count
            )

            tokenized_sample_count += len(
                tokenized_samples
            )

            processed_token_count += sum(
                len(sample.input_ids)
                for sample in tokenized_samples
            )

            if first_record_id is None:
                first_record_id = (
                    batch.first_record_id
                )

            last_record_id = (
                batch.last_record_id
            )

            processed_record_count += (
                batch.record_count
            )

            processed_batch_count += 1

            formatted_sample_count += len(
                formatted_samples
            )

            await (
                training_progress_service
                .on_batch_completed(
                    runtime=runtime,
                    context=context,
                    epoch=0,
                    step=optimizer_step_count,
                    global_step=optimizer_step_count,
                    current_loss=float(batch_loss),
                    learning_rate=None,
                    processed_samples=processed_record_count,
                    processed_tokens=processed_token_count,
                )
            )

            await context.db.commit()

            if (
                checkpoint_enabled
                and
                optimizer_step_performed
            ):

                current_step_count = int(
                    strategy_state.get(
                        "step_count",
                        optimizer_step_count,
                    )
                )

                if (
                    current_step_count > 0
                    and
                    current_step_count
                    %
                    checkpoint_every_steps
                    ==
                    0
                    and
                    current_step_count
                    !=
                    last_published_checkpoint_step
                ):

                    await (
                        training_checkpoint_service
                        .publish(
                            db=context.db,
                            runtime=runtime,
                            model=model,
                            strategy_state=(
                                strategy_state
                            ),
                            data_cursor={
                                "last_record_id": (
                                    last_record_id
                                ),
                                "processed_record_count": (
                                    processed_record_count
                                ),
                                "processed_batch_count": (
                                    processed_batch_count
                                ),
                            },
                            configuration=(
                                checkpoint_configuration
                            ),
                            organization_id=(
                                context.organization_id
                            ),
                            workspace_id=(
                                context.workspace_id
                            ),
                        )
                    )

                    await context.db.commit()

                    await (
                        training_progress_service
                        .on_checkpoint_saved(
                            runtime=runtime,
                            context=context,
                            checkpoint_path=runtime.artifact_directory,
                        )
                    )

                    await context.db.commit()



                    last_published_checkpoint_step = (
                        current_step_count
                    )

        strategy_final_metadata = await (
            training_strategy
            .finalize(
                runtime=runtime,
                model=model,
                strategy_state=strategy_state,
                configuration=(
                    strategy_configuration
                ),
            )
        )

        if not isinstance(
            strategy_final_metadata,
            dict,
        ):
            raise ValueError(
                "Training strategy finalize must "
                "return an object."
            )

        final_step_count = (
            strategy_final_metadata.get(
                "step_count"
            )
        )

        if (
            isinstance(final_step_count, bool)
            or
            not isinstance(
                final_step_count,
                int,
            )
            or
            final_step_count < 0
        ):
            raise ValueError(
                "Training strategy finalize returned "
                "an invalid step count."
            )

        optimizer_step_count = (
            final_step_count
        )

        final_artifact_configuration = (
            runtime.runtime_configuration.get(
                "final_artifact"
            )
        )

        final_artifact = None

        if final_artifact_configuration is not None:

            if not isinstance(
                final_artifact_configuration,
                dict,
            ):
                raise ValueError(
                    "'final_artifact' must be "
                    "an object."
                )

            final_artifact_enabled = (
                final_artifact_configuration.get(
                    "enabled",
                    False,
                )
            )

            if not isinstance(
                final_artifact_enabled,
                bool,
            ):
                raise ValueError(
                    "'final_artifact.enabled' "
                    "must be boolean."
                )

            if final_artifact_enabled:

                final_artifact = await (
                    training_final_artifact_service
                    .publish(
                        db=context.db,
                        runtime=runtime,
                        model=model,
                        strategy_metadata=(
                            strategy_final_metadata
                        ),
                        configuration=(
                            final_artifact_configuration
                        ),
                        organization_id=(
                            context.organization_id
                        ),
                        workspace_id=(
                            context.workspace_id
                        ),
                    )
                )

                await context.db.commit()

        if (
            processed_record_count
            !=
            runtime.snapshot_record_count
        ):
            raise ValueError(
                "Training data stream cumulative "
                "record count does not match the "
                "immutable dataset snapshot."
            )

        if (
            formatted_sample_count
            !=
            processed_record_count
        ):
            raise ValueError(
                "Formatted training sample count "
                "does not match cumulative processed "
                "training record count."
            )

        if (
            tokenized_sample_count
            !=
            formatted_sample_count
        ):
            raise ValueError(
                "Tokenized training sample count "
                "does not match formatted "
                "training sample count."
            )
        
        await (
            training_progress_service
            .on_training_completed(
                runtime=runtime,
                context=context,
            )
        )

        await context.db.commit()

        return TrainingResult(
            success=True,

            training_job_id=(
                runtime.training_job_id
            ),

            runtime_code=(
                runtime.runtime_code
            ),

            artifact_directory=(
                runtime.artifact_directory
            ),

            metrics={
                "processed_record_count": (
                    processed_record_count
                ),
                "processed_batch_count": (
                    processed_batch_count
                ),
                "formatted_sample_count": (
                    formatted_sample_count
                ),
                "tokenized_sample_count": (
                    tokenized_sample_count
                ),
                "processed_token_count": (
                    processed_token_count
                ),
                "trained_sample_count": (
                    trained_sample_count
                ),
                "micro_step_count": (
                    micro_step_count
                ),
                "optimizer_step_count": (
                    optimizer_step_count
                ),
                "average_training_loss": (
                    (
                        loss_total
                        /
                        loss_observation_count
                    )
                    if loss_observation_count > 0
                    else 0.0
                ),
            },

            runtime_metadata={
                "dataset_snapshot_id": (
                    runtime.dataset_snapshot_id
                ),
                "snapshot_content_hash": (
                    runtime.snapshot_content_hash
                ),
                "base_model_version_id": (
                    runtime.base_model_version_id
                ),
                "tokenizer_version_id": (
                    runtime.tokenizer_version_id
                ),
                "training_configuration_id": (
                    runtime.training_configuration_id
                ),
                "first_record_id": (
                    first_record_id
                ),
                "last_record_id": (
                    last_record_id
                ),
                "resumed_from_checkpoint": (
                    restored_checkpoint is not None
                ),
                "restored_checkpoint_artifact_id": (
                    restored_checkpoint.get(
                        "artifact_id"
                    )
                    if restored_checkpoint is not None
                    else None
                ),
                "sample_formatter_class": (
                    formatter_configuration.get(
                        "formatter_class"
                    )
                ),
                "tokenizer_code": (
                    tokenizer_configuration.get(
                        "tokenizer_code"
                    )
                ),
                "model_class": (
                    model.__class__.__module__
                    +
                    "."
                    +
                    model.__class__.__name__
                ),
                "trainable_parameter_count": sum(
                    parameter.numel()
                    for parameter in model.parameters()
                    if parameter.requires_grad
                ),
                "training_strategy_class": (
                    training_strategy.__class__.__module__
                    +
                    "."
                    +
                    training_strategy.__class__.__name__
                ),
                "training_strategy_metadata": (
                    strategy_final_metadata
                ),

                "final_artifact_id": (
                    final_artifact.id
                    if final_artifact is not None
                    else None
                ),

                "final_artifact_type": (
                    final_artifact.artifact_type
                    if final_artifact is not None
                    else None
                ),

                "final_artifact_checksum": (
                    final_artifact.checksum
                    if final_artifact is not None
                    else None
                ),

                "final_artifact_size_bytes": (
                    final_artifact.size_bytes
                    if final_artifact is not None
                    else None
                ),

                "final_storage_instance_id": (
                    final_artifact.storage_instance_id
                    if final_artifact is not None
                    else None
                ),

                "final_storage_reference": (
                    final_artifact.storage_reference
                    if final_artifact is not None
                    else None
                ),
            },

            message=(
                "Training execution completed "
                "successfully."
            ),
        )


native_training_runtime = (
    NativeTrainingRuntime()
)