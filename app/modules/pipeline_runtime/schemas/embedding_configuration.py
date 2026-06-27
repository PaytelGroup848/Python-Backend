from app.modules.pipeline_runtime.schemas.base_provider_configuration import (
    BaseProviderConfiguration
)


class EmbeddingConfiguration(
    BaseProviderConfiguration
):

    model_name: str

    batch_size: int

    normalize_embeddings: bool

    embedding_dimension: int | None = None