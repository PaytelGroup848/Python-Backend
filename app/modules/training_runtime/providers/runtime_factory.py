from app.modules.training_runtime.providers.base_training_runtime import (
    BaseTrainingRuntime
)

from app.modules.training_runtime.providers.native_training_runtime import (
    NativeTrainingRuntime
)


class TrainingRuntimeFactory:

    def __init__(self):

        self._registry = {}

        self.register(
            runtime_code="NATIVE",
            runtime=NativeTrainingRuntime()
        )

    def register(

        self,

        runtime_code: str,

        runtime: BaseTrainingRuntime

    ):

        self._registry[
            runtime_code.upper()
        ] = runtime

    def get_runtime(

        self,

        runtime_code: str

    ) -> BaseTrainingRuntime:

        runtime = self._registry.get(
            runtime_code.upper()
        )

        if runtime is None:

            raise ValueError(

                f"Training runtime '{runtime_code}' is not registered."

            )

        return runtime


training_runtime_factory = (
    TrainingRuntimeFactory()
)