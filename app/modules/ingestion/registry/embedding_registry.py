from app.modules.ingestion.embeddings.base_embedding_provider import (
    BaseEmbeddingProvider
)

from app.shared.exceptions.business_exception import (
    BusinessException
)

from app.modules.ingestion.embeddings.huggingface_embedding_provider import (
    huggingface_embedding_provider
)

from app.modules.ingestion.embeddings.native_embedding_provider import (
    native_embedding_provider
)

class EmbeddingRegistry:

    def __init__(
        self
    ):

        self._providers: dict[
            str,
            BaseEmbeddingProvider
        ] = {}

        self.register(
            huggingface_embedding_provider
        )

        self.register(
            native_embedding_provider
        )

    def register(
        self,
        provider: BaseEmbeddingProvider
    ) -> None:

        provider_code = (
            provider.provider_code.upper()
        )

        if provider_code in self._providers:

            raise BusinessException(

                f"Embedding provider '{provider_code}' is already registered."

            )

        self._providers[
            provider_code
        ] = provider

    def get_provider(
        self,
        provider_code: str
    ) -> BaseEmbeddingProvider:

        provider = self._providers.get(
            provider_code.upper()
        )

        if provider is None:

            raise BusinessException(

                f"Embedding provider '{provider_code}' is not registered."

            )

        return provider

    @property
    def providers(
        self
    ) -> dict[
        str,
        BaseEmbeddingProvider
    ]:

        return self._providers.copy()


embedding_registry = (
    EmbeddingRegistry()
)