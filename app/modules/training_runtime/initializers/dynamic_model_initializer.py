from copy import deepcopy

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

        if not isinstance(
            configuration,
            dict,
        ):
            raise ValueError(
                "Model initialization configuration "
                "must be an object."
            )

        model_class = (
            configuration.get(
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

        model_configuration = deepcopy(
            configuration.get(
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

        source_loader_class = (
            configuration.get(
                "source_loader_class"
            )
        )

        source_configuration = deepcopy(
            configuration.get(
                "source_configuration",
                {},
            )
        )

        if not isinstance(
            source_configuration,
            dict,
        ):
            raise ValueError(
                "'source_configuration' must be "
                "an object."
            )

        source_lineage = {
            "base_model_id": (
                runtime.base_model_id
            ),
            "base_model_version_id": (
                runtime.base_model_version_id
            ),
            "base_model_version": (
                runtime.base_model_version
            ),
            "source_type": (
                runtime.base_model_source_type
            ),
            "source_uri": (
                runtime.base_model_source_uri
            ),
            "source_revision": (
                runtime.base_model_source_revision
            ),
        }

        for key in (
            "source_type",
            "source_uri",
            "source_revision",
        ):
            value = source_lineage.get(
                key
            )

            if (
                not isinstance(value, str)
                or
                not value.strip()
            ):
                raise ValueError(
                    "Base model version has incomplete "
                    f"source lineage: {key}."
                )

        model_class_type = (
            dynamic_class_resolver
            .resolve_class(
                class_path=(
                    model_class.strip()
                ),
                expected_base_class=(
                    TrainableModel
                ),
            )
        )

        if source_loader_class is None:

            model_configuration[
                "source_lineage"
            ] = source_lineage

            model = model_class_type(
                configuration=(
                    model_configuration
                )
            )

        else:

            if (
                not isinstance(
                    source_loader_class,
                    str,
                )
                or
                not source_loader_class.strip()
            ):
                raise ValueError(
                    "'source_loader_class' must be "
                    "a non-empty class path."
                )

            source_loader_type = (
                dynamic_class_resolver
                .resolve_class(
                    class_path=(
                        source_loader_class.strip()
                    ),
                )
            )

            source_loader = (
                source_loader_type()
            )

            load_method = getattr(
                source_loader,
                "load",
                None,
            )

            if not callable(
                load_method
            ):
                raise ValueError(
                    "Configured source loader must "
                    "define load()."
                )

            loaded_source = await (
                load_method(
                    source_lineage=(
                        source_lineage
                    ),
                    configuration=(
                        source_configuration
                    ),
                )
            )

            model_configuration[
                "source_lineage"
            ] = source_lineage

            model_configuration[
                "loaded_source"
            ] = loaded_source

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

        model._training_source_lineage = (
            source_lineage
        )

        return model