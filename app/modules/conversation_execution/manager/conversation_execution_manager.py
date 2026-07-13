from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.conversation_execution.services.conversation_execution_service import (
    conversation_execution_service,
)


class ConversationExecutionManager:

    async def execute(

        self,

        db: AsyncSession,

        organization_id: int,

        workspace_id: int,

        conversation_id: int,

        content: str,

    ):

        return await (

            conversation_execution_service

            .execute(

                db=db,

                organization_id=organization_id,

                workspace_id=workspace_id,

                conversation_id=conversation_id,

                content=content,

            )

        )


conversation_execution_manager = (
    ConversationExecutionManager()
)