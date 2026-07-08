from app.shared.runtime.dynamic_class_resolver import (
    dynamic_class_resolver,
)

from app.modules.training_runtime.contracts.training_strategy import (
    TrainingStrategy,
)

from app.modules.training_runtime.contracts.trainable_model import (
    TrainableModel,
)

from app.modules.training_runtime.schemas.training_runtime_schema import (
    TrainingRuntime,
)


class TrainingStrategyService:

    async def initialize(
        self,
        runtime: TrainingRuntime,
        model: TrainableModel,
    ) -> tuple[
        TrainingStrategy,
        object,
        dict,
    ]:

        strategy_configuration = (
            runtime.runtime_configuration
            .get(
                "training_strategy"
            )
        )

        if not isinstance(
            strategy_configuration,
            dict,
        ):
            raise ValueError(
                "Training configuration must define "
                "'training_strategy' as an object."
            )

        strategy_class_path = (
            strategy_configuration
            .get(
                "strategy_class"
            )
        )

        if (
            not isinstance(
                strategy_class_path,
                str,
            )
            or
            not strategy_class_path.strip()
        ):
            raise ValueError(
                "Training strategy configuration must define "
                "'strategy_class'."
            )

        configuration = (
            strategy_configuration
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
                "Training strategy 'configuration' "
                "must be an object."
            )

        strategy_class = (
            dynamic_class_resolver
            .resolve_class(
                class_path=(
                    strategy_class_path.strip()
                ),
                expected_base_class=(
                    TrainingStrategy
                ),
            )
        )

        strategy = (
            strategy_class()
        )

        strategy_state = await (
            strategy.initialize(
                runtime=runtime,
                model=model,
                configuration=configuration,
            )
        )

        return (
            strategy,
            strategy_state,
            configuration,
        )


training_strategy_service = (
    TrainingStrategyService()
)