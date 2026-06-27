from app.modules.pipeline_runtime.schemas.base_provider_configuration import (
    BaseProviderConfiguration
)


class TokenizerConfiguration(
    BaseProviderConfiguration
):

    model_name: str | None = None

    encoding_name: str | None = None

    model_path: str | None = None

    add_special_tokens: bool | None = None

    trust_remote_code: bool | None = None