from app.modules.pipeline_runtime.executors.connector_executor import connector_executor
from app.modules.pipeline_runtime.executors.parser_executor import parser_executor
from app.modules.pipeline_runtime.executors.chunk_executor import chunk_executor
from app.modules.pipeline_runtime.executors.embedding_executor import embedding_executor
from app.modules.pipeline_runtime.executors.dataset_record_executor import (
    dataset_record_executor,
)

from app.modules.pipeline_runtime.registry.executor_registry import (
    executor_registry,
)


def register_pipeline_executors() -> None:

    executor_registry.register(
        step_type="CONNECTOR",
        executor=connector_executor,
    )

    executor_registry.register(
        step_type="PARSER",
        executor=parser_executor,
    )

    executor_registry.register(
        step_type="CHUNKER",
        executor=chunk_executor,
    )

    executor_registry.register(
        step_type="EMBEDDING",
        executor=embedding_executor,
    )

    executor_registry.register(
        step_type="DATASET_RECORD",
        executor=dataset_record_executor,
    )