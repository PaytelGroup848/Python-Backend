from app.modules.ingestion.embeddings.base_embedding_provider import (
    BaseEmbeddingProvider
)

from app.modules.pipeline_runtime.schemas.embedding_configuration import (
    EmbeddingConfiguration
)


class NativeEmbeddingProvider(
    BaseEmbeddingProvider
):

    @property
    def provider_code(
        self
    ) -> str:

        return "NATIVE"

    async def generate_embeddings(
        self,
        texts: list[str],
        configuration: EmbeddingConfiguration
    ) -> list[
        list[float]
    ]:

        raise NotImplementedError(
            "Native embedding inference engine is not implemented yet."
        )


native_embedding_provider = (
    NativeEmbeddingProvider()
)