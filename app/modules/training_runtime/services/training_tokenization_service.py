from app.modules.training_runtime.contracts.training_tokenizer import (
    TrainingTokenizer,
)

from app.modules.training_runtime.schemas.formatted_training_sample import (
    FormattedTrainingSample,
)

from app.modules.training_runtime.schemas.tokenized_training_sample import (
    TokenizedTrainingSample,
)

from app.shared.runtime.dynamic_class_resolver import (
    dynamic_class_resolver,
)


class TrainingTokenizationService:

    def tokenize_batch(
        self,
        samples: list[
            FormattedTrainingSample
        ],
        tokenizer_configuration: dict,
    ) -> list[
        TokenizedTrainingSample
    ]:

        tokenizer_class = (
            tokenizer_configuration
            .get(
                "tokenizer_class"
            )
        )

        if (
            not isinstance(
                tokenizer_class,
                str,
            )
            or
            not tokenizer_class.strip()
        ):
            raise ValueError(
                "Training tokenizer configuration must "
                "define 'tokenizer_class'."
            )

        configuration = (
            tokenizer_configuration
            .get(
                "configuration",
                {},
            )
        )

        if not isinstance(
            configuration,
            dict,
        ):
            raise ValueError(
                "Training tokenizer 'configuration' "
                "must be an object."
            )

        tokenizer_class_type = (
            dynamic_class_resolver
            .resolve_class(
                class_path=(
                    tokenizer_class
                ),
                expected_base_class=(
                    TrainingTokenizer
                ),
            )
        )

        tokenizer = (
            tokenizer_class_type()
        )

        tokenized_samples = (
            tokenizer.tokenize_batch(
                samples=samples,
                configuration=configuration,
            )
        )

        if not isinstance(
            tokenized_samples,
            list,
        ):
            raise ValueError(
                "Training tokenizer must return a list."
            )

        for sample in tokenized_samples:

            if not isinstance(
                sample,
                TokenizedTrainingSample,
            ):
                raise ValueError(
                    "Training tokenizer returned an "
                    "invalid tokenized sample."
                )

        return tokenized_samples


training_tokenization_service = (
    TrainingTokenizationService()
)