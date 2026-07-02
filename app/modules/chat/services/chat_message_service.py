from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import (
    HTTPException,
    status
)

from app.modules.chat.models.chat_message import (
    ChatMessage,
    MessageRole
)

from app.modules.chat.repositories.chat_message_repository import (
    chat_message_repository
)

from app.modules.chat.repositories.conversation_repository import (
    conversation_repository
)

from app.modules.chat.schemas.chat_message_create import (
    ChatMessageCreate
)


class ChatMessageService:

    async def create_user_message(

        self,

        db: AsyncSession,

        organization_id: int,

        workspace_id: int,

        data: ChatMessageCreate

    ) -> ChatMessage:

        #
        # Lock conversation row
        #
        conversation = await (

            conversation_repository.get_for_update(

                db=db,

                conversation_id=data.conversation_id

            )

        )

        if conversation is None:

            raise HTTPException(

                status_code=status.HTTP_404_NOT_FOUND,

                detail="Conversation not found"

            )

        #
        # Tenant validation
        #
        if conversation.organization_id != organization_id:

            raise HTTPException(

                status_code=status.HTTP_403_FORBIDDEN,

                detail="Conversation does not belong to organization"

            )

        #
        # Workspace validation
        #
        if conversation.workspace_id != workspace_id:

            raise HTTPException(

                status_code=status.HTTP_403_FORBIDDEN,

                detail="Conversation does not belong to workspace"

            )

        #
        # Safe sequence number
        #
        next_sequence = conversation.message_count + 1

        message = ChatMessage(

            organization_id=organization_id,

            workspace_id=workspace_id,

            conversation_id=conversation.id,

            sequence_number=next_sequence,

            role=MessageRole.USER,

            content=data.content

        )

        message = await (

            chat_message_repository.create(

                db=db,

                message=message

            )

        )

        #
        # Update conversation statistics
        #
        conversation.message_count += 1

        conversation.last_message_id = message.id

        conversation.last_message_at = message.created_at

        #
        # Flush only
        #
        await db.flush()

        await db.refresh(message)

        return message

    async def list_messages(

        self,

        db: AsyncSession,

        conversation_id: int

    ):

        return await (

            chat_message_repository.list_messages(

                db=db,

                conversation_id=conversation_id

            )

        )


chat_message_service = ChatMessageService()