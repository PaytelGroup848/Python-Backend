from sqlalchemy import (
    asc,
    desc,
    func,
    select
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.chat.models.chat_message import (
    ChatMessage
)


class ChatMessageRepository:

    async def create(

        self,

        db: AsyncSession,

        message: ChatMessage

    ) -> ChatMessage:

        db.add(message)

        await db.flush()

        return message

    async def list_messages(

        self,

        db: AsyncSession,

        conversation_id: int,

        limit: int = 100

    ):

        result = await db.execute(

            select(
                ChatMessage
            )

            .where(

                ChatMessage.conversation_id == conversation_id

            )

            .order_by(

                asc(
                    ChatMessage.sequence_number
                )

            )

            .limit(limit)

        )

        return result.scalars().all()

    async def get_last_sequence(

        self,

        db: AsyncSession,

        conversation_id: int

    ) -> int:

        result = await db.execute(

            select(

                func.max(
                    ChatMessage.sequence_number
                )

            )

            .where(

                ChatMessage.conversation_id == conversation_id

            )

        )

        sequence = result.scalar()

        return sequence or 0

    async def get_last_message(

        self,

        db: AsyncSession,

        conversation_id: int

    ):

        result = await db.execute(

            select(
                ChatMessage
            )

            .where(

                ChatMessage.conversation_id == conversation_id

            )

            .order_by(

                desc(
                    ChatMessage.sequence_number
                )

            )

            .limit(1)

        )

        return result.scalar_one_or_none()


chat_message_repository = (
    ChatMessageRepository()
)