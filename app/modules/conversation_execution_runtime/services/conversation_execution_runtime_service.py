from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.conversation_execution_runtime.schemas.conversation_execution_context import (
    ConversationExecutionContext,
)

from app.modules.conversation_runtime.schemas.conversation_context import (
    ConversationContext,
)

from app.modules.workspace_runtime.schemas.workspace_runtime_schema import (
    WorkspaceRuntime,
)

from app.modules.models.services.inference_runtime_service import (
    inference_runtime_service,
)


class ConversationExecutionRuntimeService:

    async def build_execution_context(

        self,

        db: AsyncSession,

        conversation: ConversationContext,

        workspace: WorkspaceRuntime,

    ) -> ConversationExecutionContext:

        inference_runtime = await (

            inference_runtime_service

            .load_runtime(

                db=db,

                model_version_id=
                    workspace.model_version_id,

            )

        )

        return ConversationExecutionContext(

            conversation=
                conversation,

            workspace=
                workspace,

            inference=
                inference_runtime,

        )


conversation_execution_runtime_service = (
    ConversationExecutionRuntimeService()
)