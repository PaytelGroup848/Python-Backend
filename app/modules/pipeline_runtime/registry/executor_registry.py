from app.modules.pipeline_runtime.executors.base_executor import (
    BaseExecutor,
)


class ExecutorRegistry:

    def __init__(
        self,
    ) -> None:

        self._executors: dict[
            str,
            BaseExecutor,
        ] = {}

    @staticmethod
    def _normalize(
        step_type: str,
    ) -> str:

        normalized = (
            step_type
            .strip()
            .upper()
        )

        if not normalized:

            raise ValueError(
                "Pipeline step type is required"
            )

        return normalized

    def register(
        self,
        step_type: str,
        executor: BaseExecutor,
    ) -> None:

        normalized = self._normalize(
            step_type
        )

        existing = self._executors.get(
            normalized
        )

        if existing is not None:

            if existing is executor:
                return

            raise ValueError(
                "Pipeline executor already registered: "
                f"{normalized}"
            )

        self._executors[
            normalized
        ] = executor

    def get_executor(
        self,
        step_type: str,
    ) -> BaseExecutor:

        normalized = self._normalize(
            step_type
        )

        executor = self._executors.get(
            normalized
        )

        if executor is None:

            raise ValueError(
                "No pipeline executor registered for: "
                f"{normalized}"
            )

        return executor


executor_registry = ExecutorRegistry()