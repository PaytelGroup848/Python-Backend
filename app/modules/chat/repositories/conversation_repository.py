from sqlalchemy import (
    desc,
    select,
    update,
)

from sqlalchemy.orm import (
    selectinload,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.chat.models.conversation import (
    Conversation,
    ConversationStatus,
)


class ConversationRepository:

    async def create(

        self,

        db: AsyncSession,

        conversation: Conversation,

    ) -> Conversation:

        db.add(conversation)

        await db.flush()

        return conversation

    async def get_by_id(

        self,

        db: AsyncSession,

        conversation_id: int,

    ) -> Conversation | None:

        result = await db.execute(

            select(Conversation)

            .where(

                Conversation.id == conversation_id,

                Conversation.deleted_at.is_(None),

            )

        )

        return result.scalar_one_or_none()

    async def get_with_messages(

        self,

        db: AsyncSession,

        conversation_id: int,

    ) -> Conversation | None:

        result = await db.execute(

            select(Conversation)

            .options(

                selectinload(
                    Conversation.messages
                )

            )

            .where(

                Conversation.id == conversation_id,

                Conversation.deleted_at.is_(None),

            )

        )

        return result.scalar_one_or_none()

    async def get_for_update(

        self,

        db: AsyncSession,

        conversation_id: int,

    ) -> Conversation | None:

        result = await db.execute(

            select(Conversation)

            .where(

                Conversation.id == conversation_id,

                Conversation.deleted_at.is_(None),

            )

            .with_for_update()

        )

        return result.scalar_one_or_none()

    async def list_by_workspace(

        self,

        db: AsyncSession,

        organization_id: int,

        workspace_id: int,

        limit: int = 20,

        cursor: int | None = None,

    ):

        query = (

            select(Conversation)

            .where(

                Conversation.organization_id == organization_id,

                Conversation.workspace_id == workspace_id,

                Conversation.deleted_at.is_(None),

            )

        )

        #
        # Cursor Pagination
        #
        if cursor:

            query = query.where(

                Conversation.id < cursor

            )

        query = (

            query

            .order_by(

                desc(
                    Conversation.id
                )

            )

            .limit(limit)

        )

        result = await db.execute(query)

        return result.scalars().all()

    async def archive(

        self,

        db: AsyncSession,

        conversation_id: int,

    ):

        await db.execute(

            update(Conversation)

            .where(

                Conversation.id == conversation_id,

                Conversation.deleted_at.is_(None),

            )

            .values(

                status=ConversationStatus.ARCHIVED

            )

        )

    async def soft_delete(

        self,

        db: AsyncSession,

        conversation_id: int,

    ):

        await db.execute(

            update(Conversation)

            .where(

                Conversation.id == conversation_id,

                Conversation.deleted_at.is_(None),

            )

            .values(

                status=ConversationStatus.DELETED

            )

        )

    async def save(

        self,

        db: AsyncSession,

        conversation: Conversation,

    ) -> Conversation:

        await db.flush()

        return conversation


conversation_repository = ConversationRepository()