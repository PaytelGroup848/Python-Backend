from app.modules.training_runtime.contracts.training_tokenizer import (
    TrainingTokenizer,
)

from app.modules.training_runtime.contracts.training_tokenization_algorithm import (
    TrainingTokenizationAlgorithm,
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


class NativeTrainingTokenizer(
    TrainingTokenizer
):

    def tokenize_batch(
        self,
        samples: list[
            FormattedTrainingSample
        ],
        configuration: dict,
    ) -> list[
        TokenizedTrainingSample
    ]:

        algorithm_class = (
            configuration
            .get(
                "algorithm_class"
            )
        )

        if (
            not isinstance(
                algorithm_class,
                str,
            )
            or
            not algorithm_class.strip()
        ):
            raise ValueError(
                "Training tokenizer configuration must "
                "define 'algorithm_class'."
            )

        algorithm_configuration = (
            configuration
            .get(
                "algorithm_configuration",
                {},
            )
        )

        if not isinstance(
            algorithm_configuration,
            dict,
        ):
            raise ValueError(
                "'algorithm_configuration' "
                "must be an object."
            )

        max_sequence_length = (
            configuration
            .get(
                "max_sequence_length"
            )
        )

        if (
            isinstance(
                max_sequence_length,
                bool,
            )
            or
            not isinstance(
                max_sequence_length,
                int,
            )
            or
            max_sequence_length <= 0
        ):
            raise ValueError(
                "'max_sequence_length' must be "
                "a positive integer."
            )

        add_bos_token = (
            configuration
            .get(
                "add_bos_token",
                False,
            )
        )

        add_eos_token = (
            configuration
            .get(
                "add_eos_token",
                False,
            )
        )

        pad_to_max_sequence_length = (
            configuration
            .get(
                "pad_to_max_sequence_length",
                False,
            )
        )

        if not isinstance(
            add_bos_token,
            bool,
        ):
            raise ValueError(
                "'add_bos_token' must be boolean."
            )

        if not isinstance(
            add_eos_token,
            bool,
        ):
            raise ValueError(
                "'add_eos_token' must be boolean."
            )

        if not isinstance(
            pad_to_max_sequence_length,
            bool,
        ):
            raise ValueError(
                "'pad_to_max_sequence_length' "
                "must be boolean."
            )

        algorithm_class_type = (
            dynamic_class_resolver
            .resolve_class(
                class_path=(
                    algorithm_class.strip()
                ),
                expected_base_class=(
                    TrainingTokenizationAlgorithm
                ),
            )
        )

        algorithm = (
            algorithm_class_type()
        )

        bos_token_id = None

        if add_bos_token:

            bos_token_id = (
                algorithm
                .get_special_token_id(
                    token_name="bos",
                    configuration=(
                        algorithm_configuration
                    ),
                )
            )

            if bos_token_id is None:
                raise ValueError(
                    "Configured tokenization algorithm "
                    "does not provide a BOS token."
                )

        eos_token_id = None

        if add_eos_token:

            eos_token_id = (
                algorithm
                .get_special_token_id(
                    token_name="eos",
                    configuration=(
                        algorithm_configuration
                    ),
                )
            )

            if eos_token_id is None:
                raise ValueError(
                    "Configured tokenization algorithm "
                    "does not provide an EOS token."
                )

        pad_token_id = None

        if pad_to_max_sequence_length:

            pad_token_id = (
                algorithm
                .get_special_token_id(
                    token_name="pad",
                    configuration=(
                        algorithm_configuration
                    ),
                )
            )

            if pad_token_id is None:
                raise ValueError(
                    "Configured tokenization algorithm "
                    "does not provide a PAD token."
                )

        tokenized_samples = []

        for sample in samples:

            input_token_ids = (
                algorithm
                .encode(
                    text=sample.input_text,
                    configuration=(
                        algorithm_configuration
                    ),
                )
            )

            if not isinstance(
                input_token_ids,
                list,
            ):
                raise ValueError(
                    "Training tokenization algorithm "
                    "must return a list of token IDs."
                )

            target_token_ids = []

            if sample.target_text is not None:

                target_token_ids = (
                    algorithm
                    .encode(
                        text=sample.target_text,
                        configuration=(
                            algorithm_configuration
                        ),
                    )
                )

                if not isinstance(
                    target_token_ids,
                    list,
                ):
                    raise ValueError(
                        "Training tokenization algorithm "
                        "must return a list of token IDs."
                    )

            sequence = []

            labels = []

            if bos_token_id is not None:

                sequence.append(
                    bos_token_id
                )

                labels.append(
                    -100
                )

            sequence.extend(
                input_token_ids
            )

            if sample.target_text is None:

                labels.extend(
                    input_token_ids
                )

            else:

                labels.extend(
                    [-100]
                    *
                    len(
                        input_token_ids
                    )
                )

                sequence.extend(
                    target_token_ids
                )

                labels.extend(
                    target_token_ids
                )

            if eos_token_id is not None:

                sequence.append(
                    eos_token_id
                )

                labels.append(
                    eos_token_id
                )

            sequence = (
                sequence[
                    :max_sequence_length
                ]
            )

            labels = (
                labels[
                    :max_sequence_length
                ]
            )

            if not sequence:
                raise ValueError(
                    "Tokenized training sequence "
                    "must not be empty."
                )

            if len(sequence) != len(labels):
                raise ValueError(
                    "Tokenized input and labels "
                    "must have equal length."
                )

            if not all(
                isinstance(
                    token_id,
                    int,
                )
                and
                not isinstance(
                    token_id,
                    bool,
                )
                for token_id in sequence
            ):
                raise ValueError(
                    "Tokenized sequence contains "
                    "an invalid token ID."
                )

            if not all(
                (
                    isinstance(
                        label,
                        int,
                    )
                    and
                    not isinstance(
                        label,
                        bool,
                    )
                )
                for label in labels
            ):
                raise ValueError(
                    "Training labels contain "
                    "an invalid token ID."
                )

            unpadded_sequence_length = (
                len(
                    sequence
                )
            )

            attention_mask = (
                [1]
                *
                unpadded_sequence_length
            )

            if (
                pad_to_max_sequence_length
                and
                unpadded_sequence_length
                <
                max_sequence_length
            ):

                padding_length = (
                    max_sequence_length
                    -
                    unpadded_sequence_length
                )

                sequence.extend(
                    [pad_token_id]
                    *
                    padding_length
                )

                labels.extend(
                    [-100]
                    *
                    padding_length
                )

                attention_mask.extend(
                    [0]
                    *
                    padding_length
                )

            if (
                len(sequence)
                !=
                len(labels)
            ):
                raise ValueError(
                    "Tokenized input and labels "
                    "must have equal length after "
                    "padding."
                )

            if (
                len(sequence)
                !=
                len(attention_mask)
            ):
                raise ValueError(
                    "Tokenized input and attention mask "
                    "must have equal length."
                )

            tokenized_samples.append(
                TokenizedTrainingSample(
                    source_record_id=(
                        sample.source_record_id
                    ),
                    input_ids=(
                        sequence
                    ),
                    attention_mask=(
                        attention_mask
                    ),
                    labels=(
                        labels
                    ),
                    metadata={
                        **sample.metadata,
                        "tokenization_algorithm_class": (
                            algorithm_class.strip()
                        ),
                        "sequence_length": (
                            len(
                                sequence
                            )
                        ),
                        "unpadded_sequence_length": (
                            unpadded_sequence_length
                        ),
                        "padding_applied": (
                            len(sequence)
                            >
                            unpadded_sequence_length
                        ),
                    },
                )
            )

        return tokenized_samples