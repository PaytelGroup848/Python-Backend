from app.modules.training_runtime.contracts.training_sample_formatter import (
    TrainingSampleFormatter,
)

from app.modules.training_runtime.schemas.formatted_training_sample import (
    FormattedTrainingSample,
)

from app.modules.training_runtime.schemas.training_data_batch import (
    TrainingDataBatch,
)

from app.shared.runtime.dynamic_class_resolver import (
    dynamic_class_resolver,
)


class TrainingSampleFormatterService:

    def format_batch(
        self,
        batch: TrainingDataBatch,
        formatter_configuration: dict,
    ) -> list[
        FormattedTrainingSample
    ]:

        formatter_class = (
            formatter_configuration
            .get(
                "formatter_class"
            )
        )

        if (
            not isinstance(
                formatter_class,
                str,
            )
            or
            not formatter_class.strip()
        ):
            raise ValueError(
                "Sample formatter configuration must define "
                "'formatter_class'."
            )

        configuration = (
            formatter_configuration
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
                "Sample formatter 'configuration' "
                "must be an object."
            )

        formatter_class_type = (
            dynamic_class_resolver
            .resolve_class(
                class_path=(
                    formatter_class.strip()
                ),
                expected_base_class=(
                    TrainingSampleFormatter
                ),
            )
        )

        formatter = (
            formatter_class_type()
        )

        formatted_samples = [
            formatter.format_record(
                record=record,
                configuration=configuration,
            )
            for record in batch.records
        ]

        for sample in formatted_samples:

            if not isinstance(
                sample,
                FormattedTrainingSample,
            ):
                raise ValueError(
                    "Training sample formatter returned "
                    "an invalid formatted sample."
                )

        return formatted_samples


training_sample_formatter_service = (
    TrainingSampleFormatterService()
)