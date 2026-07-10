from app.modules.tokenizers.contracts.tokenizer_trainer import (
    TokenizerTrainer,
)

from app.modules.tokenizers.models.tokenizer_implementation import (
    TokenizerImplementation,
)

from app.shared.runtime.dynamic_class_resolver import (
    dynamic_class_resolver,
)


class TokenizerTrainerResolutionService:

    def resolve(
        self,
        implementation: TokenizerImplementation,
    ) -> TokenizerTrainer:

        trainer_class_path = (
            implementation.trainer_class
        )

        if (
            not isinstance(
                trainer_class_path,
                str,
            )
            or
            not trainer_class_path.strip()
        ):
            raise ValueError(
                "Tokenizer implementation must define "
                "a non-empty trainer_class."
            )

        trainer_class = (
            dynamic_class_resolver
            .resolve_class(
                class_path=trainer_class_path,
                expected_base_class=TokenizerTrainer,
            )
        )

        trainer = trainer_class()

        if not isinstance(
            trainer,
            TokenizerTrainer,
        ):
            raise TypeError(
                "Resolved tokenizer trainer is invalid."
            )

        return trainer


tokenizer_trainer_resolution_service = (
    TokenizerTrainerResolutionService()
)