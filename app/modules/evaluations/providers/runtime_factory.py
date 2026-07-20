from threading import (
    Lock,
)

from app.modules.evaluations.providers.base_evaluation_runtime import (
    BaseEvaluationRuntime,
)

from app.shared.runtime.dynamic_class_resolver import (
    dynamic_class_resolver,
)


class EvaluationRuntimeFactory:

    def __init__(
        self,
    ):

        self._runtime_cache: dict[
            str,
            BaseEvaluationRuntime
        ] = {}

        self._lock = Lock()

    def get_runtime(
        self,
        runtime_class: str,
    ) -> BaseEvaluationRuntime:

        normalized_runtime_class = (
            runtime_class.strip()
        )

        if not normalized_runtime_class:

            raise ValueError(
                "Evaluation runtime class is required."
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
                        BaseEvaluationRuntime
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


evaluation_runtime_factory = (
    EvaluationRuntimeFactory()
)