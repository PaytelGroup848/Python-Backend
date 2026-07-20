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

        chunks: list[DocumentChunk] = []

        for item in context.inputs:

            if not item:
                continue

            try:

                chunk = DocumentChunk.model_validate(
                    item
                )

            except Exception as ex:

                raise ValueError(
                    f"Invalid document chunk: {ex}"
                )

            if not chunk.content.strip():
                continue

        chunks.append(chunk)

        if not chunks:

            return ExecutorResult(

                metrics={
                    "input_count": 0,
                    "embedding_count": 0,
                    "embedding_dimension": 0,
                },

                outputs=[],
            )

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

        if len(vectors) != len(chunks):

            raise ValueError(
                "Embedding count mismatch."
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

            metadata = payload.get("metadata") or {}

            metadata["embedding_provider"] = provider_code

            metadata["embedding_dimension"] = len(vector)

            metadata["pipeline_step"] = (
                context.pipeline_step.step_code
            )

            payload["metadata"] = metadata

            payload["dataset_id"] = (
                context.dataset.id
                if context.dataset
                else None
            )

            payload["corpus_source_id"] = (
                context.corpus_source.id
                if context.corpus_source
                else None
            )

            outputs.append(
                payload
            )

        return ExecutorResult(
            metrics={

                "input_count": len(chunks),

                "output_count": len(outputs),

                "embedding_count": len(vectors),

                "embedding_dimension": (
                    len(vectors[0])
                    if vectors
                    else 0
                ),

                "provider": provider_code,
            },
            outputs=outputs,
        )


embedding_executor = EmbeddingExecutor()