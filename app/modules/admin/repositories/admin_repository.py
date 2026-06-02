from sqlalchemy import func
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.conversation_session import (
    ConversationSession
)

from app.models.message import Message


class AdminRepository:

    async def get_dashboard_metrics(
        self,
        db: AsyncSession,
    ):

        users_result = await db.execute(
            select(
                func.count(User.id)
            )
        )

        conversations_result = await db.execute(
            select(
                func.count(
                    ConversationSession.id
                )
            )
        )

        messages_result = await db.execute(
            select(
                func.count(
                    Message.id
                )
            )
        )

        total_users = (
            users_result.scalar() or 0
        )

        total_conversations = (
            conversations_result.scalar() or 0
        )

        total_messages = (
            messages_result.scalar() or 0
        )

        return {
            "total_users":
                total_users,

            "total_conversations":
                total_conversations,

            "total_messages":
                total_messages,

            "active_providers":
                5,

            "active_workers":
                4,
        }