from app.modules.ingestion.registry.embedding_registry import (
    embedding_registry
)

from app.modules.pipeline_runtime.schemas.embedding_configuration import (
    EmbeddingConfiguration
)

from app.shared.exceptions.business_exception import (
    BusinessException
)


class EmbeddingExecutionService:

    async def generate_embeddings(
        self,
        texts: list[str],
        provider_code: str,
        configuration: EmbeddingConfiguration
    ) -> list[
        list[float]
    ]:

        provider = (
            embedding_registry.get_provider(
                provider_code
            )
        )

        embeddings = (
            await provider.generate_embeddings(
                texts=texts,
                configuration=configuration
            )
        )

        if len(
            embeddings
        ) != len(
            texts
        ):

            raise BusinessException(

                "Embedding provider returned an invalid number of embeddings."

            )

        return embeddings


embedding_execution_service = (
    EmbeddingExecutionService()
)