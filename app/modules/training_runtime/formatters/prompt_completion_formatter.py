from app.modules.training_runtime.contracts.training_sample_formatter import (
    TrainingSampleFormatter,
)

from app.modules.training_runtime.schemas.training_data_record import (
    TrainingDataRecord,
)

from app.modules.training_runtime.schemas.formatted_training_sample import (
    FormattedTrainingSample,
)


class PromptCompletionFormatter(
    TrainingSampleFormatter
):

    FORMATTER_CODE = (
        "PROMPT_COMPLETION"
    )

    def format_record(
        self,
        record: TrainingDataRecord,
        configuration: dict,
    ) -> FormattedTrainingSample:

        require_target = (
            configuration.get(
                "require_target",
                True,
            )
        )

        if not isinstance(
            require_target,
            bool,
        ):
            raise ValueError(
                "'require_target' must be a boolean."
            )

        input_text = (
            record.input_text.strip()
        )

        if not input_text:
            raise ValueError(
                "Training record input_text cannot be empty."
            )

        target_text = (
            record.output_text.strip()
            if record.output_text
            else None
        )

        if (
            require_target
            and
            not target_text
        ):
            raise ValueError(
                "Training record output_text is required "
                "by the selected formatter configuration."
            )

        return FormattedTrainingSample(
            source_record_id=(
                record.record_id
            ),

            formatter_code=(
                self.FORMATTER_CODE
            ),

            input_text=input_text,

            target_text=target_text,

            metadata={
                **record.metadata,

                "record_type": (
                    record.record_type
                ),
            },
        )