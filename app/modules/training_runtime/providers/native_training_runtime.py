from app.modules.training_runtime.contracts.training_data_stream import (
    TrainingDataStream,
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

from app.modules.training_runtime.services.training_sample_formatter_service import (
    training_sample_formatter_service,
)

from app.modules.training_runtime.services.training_tokenization_service import (
    training_tokenization_service,
)

from app.modules.training_runtime.services.training_model_initialization_service import (
    training_model_initialization_service,
)
from app.modules.training_runtime.contracts.trainable_model import (
    TrainableModel,
)

from app.modules.training_runtime.services.training_strategy_service import (
    training_strategy_service,
)


class NativeTrainingRuntime(
    BaseTrainingRuntime
):

    async def execute(
        self,
        runtime: TrainingRuntime,
        training_data: TrainingDataStream,
    ) -> TrainingResult:

        processed_record_count = 0

        processed_batch_count = 0

        formatted_sample_count = 0

        first_record_id: int | None = None

        last_record_id: int | None = None

        formatter_configuration = (
            runtime.runtime_configuration
            .get(
                "sample_formatter"
            )
        )

        if not isinstance(
            formatter_configuration,
            dict,
        ):
            raise ValueError(
                "Training configuration must define "
                "'sample_formatter' as an object."
            )
        
        tokenizer_configuration = (
            runtime.runtime_configuration
            .get(
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

        tokenized_sample_count = 0

        processed_token_count = 0

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

        training_step_count = 0

        training_loss_total = 0.0

        trained_sample_count = 0

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
                    strategy_state=strategy_state,
                    samples=tokenized_samples,
                    configuration=(
                        strategy_configuration
                    ),
                )
            )

            batch_loss = (
                batch_training_metrics
                .get(
                    "loss"
                )
            )

            if not isinstance(
                batch_loss,
                (int, float),
            ):
                raise ValueError(
                    "Training strategy returned an invalid loss."
                )

            training_loss_total += float(
                batch_loss
            )

            batch_trained_sample_count = (
                batch_training_metrics
                .get(
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
                    "Training strategy returned an invalid "
                    "sample count."
                )

            trained_sample_count += (
                batch_trained_sample_count
            )

            training_step_count += 1

            tokenized_sample_count += (
                len(
                    tokenized_samples
                )
            )

            processed_token_count += sum(
                len(
                    sample.input_ids
                )
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

            formatted_sample_count += (
                len(
                    formatted_samples
                )
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
                "Training strategy finalize must return "
                "an object."
            )

        if (
            processed_record_count
            !=
            runtime.snapshot_record_count
        ):

            raise ValueError(
                "Training data stream record count does not "
                "match the immutable dataset snapshot."
            )

        if (
            formatted_sample_count
            !=
            processed_record_count
        ):
            raise ValueError(
                "Formatted training sample count does not "
                "match processed training record count."
            )
        
        if (
            tokenized_sample_count
            !=
            formatted_sample_count
        ):
            raise ValueError(
                "Tokenized training sample count does not "
                "match formatted training sample count."
            )

        artifact_directory = (
            runtime.artifact_directory
            or
            f"artifacts/{runtime.training_job_id}"
        )

        return TrainingResult(
            success=True,

            training_job_id=(
                runtime.training_job_id
            ),

            runtime_code=(
                runtime.runtime_code
            ),

            artifact_directory=(
                artifact_directory
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

                "training_step_count": (
                    training_step_count
                ),

                "trained_sample_count": (
                    trained_sample_count
                ),

                "average_training_loss": (
                    (
                        training_loss_total
                        /
                        training_step_count
                    )
                    if training_step_count > 0
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

                "first_record_id": (
                    first_record_id
                ),

                "last_record_id": (
                    last_record_id
                ),

                "sample_formatter_code": (
                    formatter_configuration
                    .get(
                        "formatter_code"
                    )
                ),
                "tokenizer_code": (
                    tokenizer_configuration
                    .get(
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

                "trainable_parameter_count": (
                    sum(
                        parameter.numel()
                        for parameter in model.parameters()
                        if parameter.requires_grad
                    )
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
            },

            message=(
                "Training data stream formatted "
                "successfully."
            ),
        )


native_training_runtime = (
    NativeTrainingRuntime()
)