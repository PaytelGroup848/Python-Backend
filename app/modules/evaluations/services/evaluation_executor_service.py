from app.modules.evaluations.providers.runtime_factory import (
    evaluation_runtime_factory,
)

from app.modules.evaluations.services.evaluation_dataset_service import (
    evaluation_dataset_service,
)


class EvaluationExecutorService:

    async def execute(
        self,
        *,
        runtime,
        context,
    ):

        evaluation_data = await (
            evaluation_dataset_service.load(
                runtime=runtime,
                context=context,
            )
        )

        runtime_provider = (
            evaluation_runtime_factory.get_runtime(
                runtime.runtime_class,
            )
        )

        return await runtime_provider.execute(
            runtime=runtime,
            evaluation_data=evaluation_data,
            context=context,
        )


evaluation_executor_service = (
    EvaluationExecutorService()
)