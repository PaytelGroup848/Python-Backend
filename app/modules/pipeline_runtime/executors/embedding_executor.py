from copy import deepcopy
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ingestion.schemas.document_chunk import (
    DocumentChunk,
)

from app.modules.ingestion.services.embedding_execution_service import (
    embedding_execution_service,
)

from app.modules.pipeline_runtime.executors.base_executor import (
    BaseExecutor,
)

from app.modules.pipeline_runtime.schemas.embedding_configuration import (
    EmbeddingConfiguration,
)

from app.modules.pipeline_runtime.schemas.executor_result import (
    ExecutorResult,
)

from app.modules.pipeline_runtime.schemas.pipeline_execution_context import (
    PipelineExecutionContext,
)


class EmbeddingExecutor(
    BaseExecutor,
):

    async def execute(
        self,
        db: AsyncSession,
        context: PipelineExecutionContext,
    ) -> ExecutorResult:

        configuration = EmbeddingConfiguration.model_validate(
            deepcopy(
                context.pipeline_step.configuration_json
                or {}
            )
        )

        provider_code = (
            context.pipeline_step.runtime_code
        )

        if not provider_code:
            raise ValueError(
                "Embedding provider runtime_code is required."
            )

        chunks: list[DocumentChunk] = [
            DocumentChunk.model_validate(
                item
            )
            for item in context.inputs
        ]

        texts = [
            chunk.content
            for chunk in chunks
        ]

        vectors = await (
            embedding_execution_service.generate_embeddings(
                texts=texts,
                provider_code=provider_code,
                configuration=configuration,
            )
        )

        outputs: list[
            dict[str, Any]
        ] = []

        for chunk, vector in zip(
            chunks,
            vectors,
        ):

            payload = chunk.model_dump()

            payload["embedding"] = vector

            payload["embedding_dimension"] = len(
                vector
            )

            outputs.append(
                payload
            )

        return ExecutorResult(
            metrics={
                "input_count": len(chunks),
                "embedding_count": len(vectors),
                "embedding_dimension": (
                    len(vectors[0])
                    if vectors
                    else 0
                ),
            },
            outputs=outputs,
        )


embedding_executor = EmbeddingExecutor()