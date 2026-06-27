from app.modules.pipeline_runtime.schemas.base_provider_configuration import (
    BaseProviderConfiguration
)


class ChunkConfiguration(
    BaseProviderConfiguration
):

    tokenizer_code: str

    nlp_provider_code: str

    nlp_model_name: str

    max_characters: int

    overlap_characters: int