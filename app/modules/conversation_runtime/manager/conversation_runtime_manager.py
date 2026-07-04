from app.modules.chat.models.chat_message import (
    ChatMessage,
)

from app.modules.conversation_runtime.schemas.conversation_context import (
    ConversationContext,
    ConversationMessage,
)

from app.modules.chat.models.conversation import Conversation


class ConversationManager:

    async def build_context(

        self,

        conversation: Conversation,

        messages: list[ChatMessage],

    ) -> ConversationContext:

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


conversation_manager = ConversationManager()