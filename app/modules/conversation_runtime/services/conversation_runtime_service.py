from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.core.config import (
    settings
)

from app.modules.chat.repositories.conversation_repository import (
    conversation_repository
)

from app.modules.conversation_runtime.schemas.conversation_context import (
    ConversationContext,
    ConversationMessage,
)


class ConversationRuntimeService:

    async def prepare_context(

        self,

        db: AsyncSession,

        conversation_id: int

    ) -> ConversationContext:

        conversation = await (

            conversation_repository.get_with_messages(

                db=db,

                conversation_id=conversation_id

            )

        )

        if conversation is None:

            raise HTTPException(

                status_code=status.HTTP_404_NOT_FOUND,

                detail="Conversation not found"

            )

        messages = sorted(

            conversation.messages,

            key=lambda message: message.sequence_number

        )[-settings.CONVERSATION_CONTEXT_LIMIT:]

        context_messages = [

            ConversationMessage(

                role=message.role.value,

                content=message.content,

            )

            for message in messages

        ]

        return ConversationContext(

            conversation_id=conversation.id,

            workspace_id=conversation.workspace_id,

            organization_id=conversation.organization_id,

            messages=context_messages,

        )


conversation_runtime_service = (
    ConversationRuntimeService()
)