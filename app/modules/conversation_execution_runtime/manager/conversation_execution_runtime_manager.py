from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.conversation_execution_runtime.schemas.conversation_execution_context import (
    ConversationExecutionContext,
)

from app.modules.conversation_execution_runtime.services.conversation_execution_runtime_service import (
    conversation_execution_runtime_service,
)

from app.modules.conversation_runtime.schemas.conversation_context import (
    ConversationContext,
)

from app.modules.workspace_runtime.schemas.workspace_runtime_schema import (
    WorkspaceRuntime,
)


class ConversationExecutionRuntimeManager:

    async def resolve(

        self,

        db: AsyncSession,

        conversation: ConversationContext,

        workspace: WorkspaceRuntime,

    ) -> ConversationExecutionContext:

        return await (

            conversation_execution_runtime_service

            .build_execution_context(

                db=db,

                conversation=conversation,

                workspace=workspace,

            )

        )


conversation_execution_runtime_manager = (
    ConversationExecutionRuntimeManager()
)