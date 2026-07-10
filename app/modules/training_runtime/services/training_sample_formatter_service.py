from copy import (
    deepcopy,
)

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

        if not isinstance(
            formatter_configuration,
            dict,
        ):
            raise ValueError(
                "formatter_configuration must be an object."
            )

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

        formatter_class_path = (
            formatter_class.strip()
        )

        formatter_class_type = (
            dynamic_class_resolver
            .resolve_class(
                class_path=formatter_class_path,
                expected_base_class=(
                    TrainingSampleFormatter
                ),
            )
        )

        formatter = (
            formatter_class_type()
        )

        formatted_samples: list[
            FormattedTrainingSample
        ] = []

        seen_source_record_ids: set[int] = set()

        for record in batch.records:

            if record.record_id in seen_source_record_ids:
                raise ValueError(
                    "Training batch contains duplicate "
                    "record identifiers."
                )

            seen_source_record_ids.add(
                record.record_id
            )

            sample = formatter.format_record(
                record=record,
                configuration=deepcopy(
                    configuration
                ),
            )

            if not isinstance(
                sample,
                FormattedTrainingSample,
            ):
                raise ValueError(
                    "Training sample formatter returned "
                    "an invalid formatted sample."
                )

            if (
                sample.source_record_id
                !=
                record.record_id
            ):
                raise ValueError(
                    "Formatted sample source_record_id "
                    "does not match the source record."
                )

            if not sample.input_text.strip():
                raise ValueError(
                    "Formatted sample input_text "
                    "cannot be empty."
                )

            sample.metadata = {
                **sample.metadata,
                "formatter_class": (
                    formatter_class_path
                ),
            }

            formatted_samples.append(
                sample
            )

        if (
            len(formatted_samples)
            !=
            batch.record_count
        ):
            raise ValueError(
                "Formatted sample count does not match "
                "the training batch record count."
            )

        return formatted_samples


training_sample_formatter_service = (
    TrainingSampleFormatterService()
)