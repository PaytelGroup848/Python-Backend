from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.chat.repositories.conversation_repository import (
    conversation_repository
)

from app.modules.chat.repositories.chat_message_repository import (
    chat_message_repository
)

from app.modules.conversation_runtime.manager.conversation_manager import (
    conversation_manager
)

from app.modules.conversation_runtime.schemas.conversation_context import (
    ConversationContext
)


class ConversationRuntimeService:

    async def prepare_context(

        self,

        db: AsyncSession,

        conversation_id: int

    ) -> ConversationContext:

        conversation = await (

            conversation_repository.get_by_id(

                db=db,

                conversation_id=conversation_id

            )

        )

        if conversation is None:

            raise HTTPException(

                status_code=status.HTTP_404_NOT_FOUND,

                detail="Conversation not found"

            )

        messages = await (

            chat_message_repository.list_messages(

                db=db,

                conversation_id=conversation_id,

                limit=200

            )

        )

        return await (

            conversation_manager.build_context(

                conversation=conversation,

                messages=messages

            )

        )


conversation_runtime_service = (
    ConversationRuntimeService()
)