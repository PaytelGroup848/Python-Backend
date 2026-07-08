from threading import (
    Lock,
)

from app.modules.training_runtime.providers.base_training_runtime import (
    BaseTrainingRuntime,
)

from app.shared.runtime.dynamic_class_resolver import (
    dynamic_class_resolver,
)


class TrainingRuntimeFactory:

    def __init__(
        self,
    ):

        self._runtime_cache: dict[
            str,
            BaseTrainingRuntime
        ] = {}

        self._lock = Lock()


    def get_runtime(
        self,
        runtime_class: str,
    ) -> BaseTrainingRuntime:

        normalized_runtime_class = (
            runtime_class.strip()
        )

        if not normalized_runtime_class:

            raise ValueError(
                "Training runtime class is required."
            )

        cached_runtime = (
            self._runtime_cache.get(
                normalized_runtime_class
            )
        )

        if cached_runtime is not None:

            return cached_runtime

        with self._lock:

            cached_runtime = (
                self._runtime_cache.get(
                    normalized_runtime_class
                )
            )

            if cached_runtime is not None:

                return cached_runtime

            runtime_class_type = (
                dynamic_class_resolver
                .resolve_class(
                    class_path=(
                        normalized_runtime_class
                    ),
                    expected_base_class=(
                        BaseTrainingRuntime
                    ),
                )
            )

            runtime = (
                runtime_class_type()
            )

            self._runtime_cache[
                normalized_runtime_class
            ] = runtime

            return runtime


training_runtime_factory = (
    TrainingRuntimeFactory()
)