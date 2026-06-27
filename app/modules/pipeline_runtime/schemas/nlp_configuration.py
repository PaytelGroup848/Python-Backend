from app.modules.pipeline_runtime.schemas.base_provider_configuration import (
    BaseProviderConfiguration
)


class NLPConfiguration(
    BaseProviderConfiguration
):

    model_name: str