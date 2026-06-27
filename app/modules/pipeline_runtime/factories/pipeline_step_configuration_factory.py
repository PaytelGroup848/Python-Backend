from typing import Type
from typing import TypeVar

from pydantic import BaseModel
from pydantic import ValidationError

from app.modules.pipeline_runtime.schemas.pipeline_step_runtime_configuration import (
    PipelineStepRuntimeConfiguration
)

from app.shared.exceptions.business_exception import (
    BusinessException
)


T = TypeVar(
    "T",
    bound=BaseModel
)


class PipelineStepConfigurationFactory:

    def build(
        self,
        runtime_configuration: PipelineStepRuntimeConfiguration,
        configuration_class: Type[T]
    ) -> T:

        try:

            return configuration_class.model_validate(

                runtime_configuration.configuration

            )

        except ValidationError as exception:

            raise BusinessException(

                f"Invalid runtime configuration: {exception}"

            ) from exception


pipeline_step_configuration_factory = (
    PipelineStepConfigurationFactory()
)