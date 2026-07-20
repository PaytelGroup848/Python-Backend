from app.modules.evaluations.contracts.evaluation_data_stream import (
    EvaluationDataStream,
)

from app.modules.evaluations.providers.base_evaluation_runtime import (
    BaseEvaluationRuntime,
)

from app.modules.evaluations.schemas.evaluation_execution_context import (
    EvaluationExecutionContext,
)

from app.modules.evaluations.schemas.evaluation_result_schema import (
    EvaluationResult,
)

from app.modules.evaluations.schemas.evaluation_runtime_schema import (
    EvaluationRuntime,
)


from app.modules.evaluations.services.evaluation_metric_service import (
    evaluation_metric_service,
)

from app.modules.evaluations.services.evaluation_report_service import (
    evaluation_report_service,
)

from app.modules.evaluations.services.evaluation_status_service import (
    evaluation_status_service,
)


class NativeEvaluationRuntime(
    BaseEvaluationRuntime,
):

    async def execute(
        self,
        runtime: EvaluationRuntime,
        evaluation_data: EvaluationDataStream,
        context: EvaluationExecutionContext,
    ) -> EvaluationResult:

        await evaluation_status_service.started(
            runtime=runtime,
            context=context,
        )

        #
        # TODO:
        # Load model artifact
        #

        #
        # TODO:
        # Execute inference
        #

        predictions = []
        references = []

        async for record in evaluation_data.stream():

            #
            # TODO
            # Model inference
            #

            predictions.append(None)

            references.append(
                record.expected_output
            )

        metrics = await (
            evaluation_metric_service.evaluate(
                runtime=runtime,
                predictions=predictions,
                references=references,
            )
        )

        report = await (
            evaluation_report_service.generate(
                runtime=runtime,
                metrics=metrics,
            )
        )

        await evaluation_status_service.completed(
            runtime=runtime,
            context=context,
        )

        return EvaluationResult(
            metrics=metrics,
            summary=report,
        )


native_evaluation_runtime = (
    NativeEvaluationRuntime()
)