from typing import Dict

from app.modules.pipeline_runtime.executors.base_executor import (
    BaseExecutor
)

from app.modules.pipeline_runtime.executors.connector_executor import (
    connector_executor
)

from app.shared.enums.pipeline_step_type import (
    PipelineStepType
)


class ExecutorRegistry:

    def __init__(self):

        self._executors: Dict[str, BaseExecutor] = {}

        self.register(
            PipelineStepType.CONNECTOR.value,
            connector_executor
        )

    def register(
        self,
        step_type: str,
        executor: BaseExecutor
    ):

        self._executors[step_type] = executor

    def get_executor(
        self,
        step_type: str
    ) -> BaseExecutor:

        executor = self._executors.get(
            step_type
        )

        if executor is None:

            raise ValueError(
                f"No executor registered for '{step_type}'"
            )

        return executor


executor_registry = ExecutorRegistry()