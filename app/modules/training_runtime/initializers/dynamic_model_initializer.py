from app.modules.training_runtime.contracts.trainable_model import (
    TrainableModel,
)

from app.modules.training_runtime.contracts.training_model_initializer import (
    TrainingModelInitializer,
)

from app.modules.training_runtime.schemas.training_runtime_schema import (
    TrainingRuntime,
)

from app.shared.runtime.dynamic_class_resolver import (
    dynamic_class_resolver,
)


class DynamicModelInitializer(
    TrainingModelInitializer
):

    async def initialize(
        self,
        runtime: TrainingRuntime,
        configuration: dict,
    ) -> TrainableModel:

        model_class = (
            configuration
            .get(
                "model_class"
            )
        )

        if (
            not isinstance(
                model_class,
                str,
            )
            or
            not model_class.strip()
        ):
            raise ValueError(
                "Model initialization configuration must "
                "define 'model_class'."
            )

        model_configuration = (
            configuration
            .get(
                "model_configuration",
                {},
            )
        )

        if not isinstance(
            model_configuration,
            dict,
        ):
            raise ValueError(
                "'model_configuration' must be an object."
            )

        model_class_type = (
            dynamic_class_resolver
            .resolve_class(
                class_path=model_class,
                expected_base_class=(
                    TrainableModel
                ),
            )
        )

        model = model_class_type(
            configuration=(
                model_configuration
            )
        )

        if not isinstance(
            model,
            TrainableModel,
        ):
            raise ValueError(
                "Configured model class did not produce "
                "a TrainableModel instance."
            )

        return model