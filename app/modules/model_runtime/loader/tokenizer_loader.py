from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.model_artifacts.models.model_artifact import (
    ModelArtifact,
)

from app.modules.training_runtime.services.training_runtime_service import (
    training_runtime_service,
)

from app.modules.training_runtime.tokenizers.native_training_tokenizer import (
    NativeTrainingTokenizer,
)


class TokenizerLoader:

    async def load(

        self,

        db: AsyncSession,

        artifact: ModelArtifact,

    ):

        #
        # Rebuild the same runtime used during training
        #

        training_runtime = await (

            training_runtime_service.load_runtime(

                db=db,

                training_job_id=(
                    artifact.training_job_id
                ),

            )

        )

        #
        # Resolve tokenizer configuration
        #

        tokenizer_configuration = (

            training_runtime
            .runtime_configuration
            .get(
                "tokenizer"
            )

        )

        if not isinstance(
            tokenizer_configuration,
            dict,
        ):

            raise ValueError(
                "Training runtime does not define tokenizer configuration."
            )

        #
        # Create tokenizer
        #

        tokenizer = NativeTrainingTokenizer(

            configuration=(
                tokenizer_configuration
            )

        )

        return tokenizer


tokenizer_loader = (
    TokenizerLoader()
)