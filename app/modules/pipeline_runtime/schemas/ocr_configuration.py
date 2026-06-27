from app.modules.pipeline_runtime.schemas.base_provider_configuration import (
    BaseProviderConfiguration
)


class OCRConfiguration(
    BaseProviderConfiguration
):

    language: str

    use_angle_cls: bool

    use_gpu: bool