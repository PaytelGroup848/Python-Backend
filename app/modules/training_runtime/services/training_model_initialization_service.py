from typing import (
    Any,
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


class TrainingModelInitializationService:

    async def initialize(
        self,
        runtime: TrainingRuntime,
    ) -> Any:

        initialization_configuration = (
            runtime.runtime_configuration
            .get(
                "model_initialization"
            )
        )

        print(
            "[MODEL_INIT] runtime_configuration =",
            runtime.runtime_configuration,
            flush=True,
        )

        print(
            "[MODEL_INIT] model_initialization =",
            initialization_configuration,
            flush=True,
        )

        if not isinstance(
            initialization_configuration,
            dict,
        ):
            raise ValueError(
                "Training configuration must define "
                "'model_initialization' as an object."
            )

        initializer_class = (
            initialization_configuration
            .get(
                "initializer_class"
            )
        )

        print(
            "[MODEL_INIT] initializer_class =",
            initializer_class,
            flush=True,
        )

        if (
            not isinstance(
                initializer_class,
                str,
            )
            or
            not initializer_class.strip()
        ):
            raise ValueError(
                "Model initialization configuration must "
                "define 'initializer_class'."
            )

        model_configuration = (
            initialization_configuration
            .get(
                "configuration",
                {},
            )
        )

        if not isinstance(
            model_configuration,
            dict,
        ):
            raise ValueError(
                "Model initialization 'configuration' "
                "must be an object."
            )

        print(
            "[MODEL_INIT] Resolving class:",
            initializer_class,
            flush=True,
        )

        initializer_class_type = (
            dynamic_class_resolver
            .resolve_class(
                class_path=(
                    initializer_class
                ),
                expected_base_class=(
                    TrainingModelInitializer
                ),
            )
        )

        initializer = (
            initializer_class_type()
        )

        print(
            "[MODEL_INIT] Initializer instance:",
            initializer.__class__.__name__,
            flush=True,
        )

        return await (
            initializer
            .initialize(
                runtime=runtime,
                configuration=(
                    model_configuration
                ),
            )
        )


training_model_initialization_service = (
    TrainingModelInitializationService()
)