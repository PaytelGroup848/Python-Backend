from app.modules.evaluations.providers.runtime_factory import (
    evaluation_runtime_factory,
)


class EvaluationRuntimeService:

    def get_runtime(
        self,
        runtime_class: str,
    ):

        return (
            evaluation_runtime_factory.get_runtime(
                runtime_class
            )
        )


evaluation_runtime_service = (
    EvaluationRuntimeService()
)