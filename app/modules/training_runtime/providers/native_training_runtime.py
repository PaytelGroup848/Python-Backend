from app.modules.training_runtime.providers.base_training_runtime import (
    BaseTrainingRuntime
)

from app.modules.training_runtime.schemas.training_runtime_schema import (
    TrainingRuntime
)

from app.modules.training_runtime.schemas.training_result_schema import (
    TrainingResult
)


class NativeTrainingRuntime(BaseTrainingRuntime):

    async def execute(
        self,
        runtime: TrainingRuntime
    ) -> TrainingResult:

        #
        # Dataset Loader
        #

        #
        # Tokenizer
        #

        #
        # Vocabulary
        #

        #
        # Transformer
        #

        #
        # Optimizer
        #

        #
        # Checkpoint Manager
        #

        artifact_directory = (
            f"artifacts/{runtime.training_job_id}"
        )

        return TrainingResult(

            success=True,

            training_job_id=
                runtime.training_job_id,

            runtime_code=
                runtime.provider_code,

            artifact_directory=
                artifact_directory,

            metrics={},

            runtime_metadata={},

            message=
                "Training completed successfully."
        )