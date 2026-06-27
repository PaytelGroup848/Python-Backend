from abc import (
    ABC,
    abstractmethod
)

from app.modules.pipeline_runtime.schemas.embedding_configuration import (
    EmbeddingConfiguration
)


class BaseEmbeddingProvider(
    ABC
):

    @property
    @abstractmethod
    def provider_code(
        self
    ) -> str:
        """
        Unique embedding provider identifier.
        """
        raise NotImplementedError

    @abstractmethod
    async def generate_embeddings(
        self,
        texts: list[str],
        configuration: EmbeddingConfiguration
    ) -> list[list[float]]:
        """
        Generate vector embeddings for a batch of texts.
        """
        raise NotImplementedError