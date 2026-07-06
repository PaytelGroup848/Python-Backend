from app.modules.pipeline_runtime.executors.connector_executor import (
    connector_executor,
)

from app.modules.pipeline_runtime.registry.executor_registry import (
    executor_registry,
)


def register_pipeline_executors() -> None:

    executor_registry.register(
        step_type="CONNECTOR",
        executor=connector_executor,
    )