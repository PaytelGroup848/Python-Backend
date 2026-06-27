from app.modules.ingestion.embeddings.base_embedding_provider import (
    BaseEmbeddingProvider
)

from app.modules.pipeline_runtime.schemas.embedding_configuration import (
    EmbeddingConfiguration
)

from app.shared.factories.embedding_model_factory import (
    embedding_model_factory
)


class HuggingFaceEmbeddingProvider(
    BaseEmbeddingProvider
):

    @property
    def provider_code(
        self
    ) -> str:

        return "HUGGINGFACE"

    async def generate_embeddings(
        self,
        texts: list[str],
        configuration: EmbeddingConfiguration
    ) -> list[
        list[float]
    ]:

        model = (
            embedding_model_factory.get_sentence_transformer(
                configuration.model_name
            )
        )

        embeddings = model.encode(

            sentences=texts,

            batch_size=configuration.batch_size,

            normalize_embeddings=configuration.normalize_embeddings,

            convert_to_numpy=True,

            show_progress_bar=False

        )

        return embeddings.tolist()


huggingface_embedding_provider = (
    HuggingFaceEmbeddingProvider()
)