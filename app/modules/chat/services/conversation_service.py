from fastapi import (
    HTTPException,
    status,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.shared.context.request_context import (
    RequestContext,
)

from app.modules.chat.models.conversation import (
    Conversation,
)

from app.modules.chat.repositories.conversation_repository import (
    conversation_repository,
)

from app.modules.chat.schemas.conversation_create import (
    ConversationCreate,
)

from app.modules.chat.schemas.conversation_update import (
    ConversationUpdate,
)


class ConversationService:

    async def create_conversation(

        self,

        db: AsyncSession,

        context: RequestContext,

        data: ConversationCreate,

    ) -> Conversation:

        if context.workspace is None:

            raise HTTPException(

                status_code=status.HTTP_400_BAD_REQUEST,

                detail="No active workspace selected",

            )

        conversation = Conversation(

            organization_id=context.organization.id,

            workspace_id=context.workspace.id,

            assistant_id=data.assistant_id,

            created_by=context.user.id,

            title=data.title,

        )

        conversation = await conversation_repository.create(

            db=db,

            conversation=conversation,

        )

        await db.commit()

        await db.refresh(conversation)

        return conversation

    async def get_conversation(

        self,

        db: AsyncSession,

        conversation_id: int,

    ) -> Conversation | None:

        return await conversation_repository.get_by_id(

            db=db,

            conversation_id=conversation_id,

        )

    async def list_workspace_conversations(

        self,

        db: AsyncSession,

        organization_id: int,

        workspace_id: int,

        assistant_id: int | None = None,

        limit: int = 20,

        cursor: int | None = None,

    ):

        return await conversation_repository.list_by_workspace(

            db=db,

            organization_id=organization_id,

            workspace_id=workspace_id,

            assistant_id=assistant_id,

            limit=limit,

            cursor=cursor,

        )

    async def update_conversation(

        self,

        db: AsyncSession,

        conversation: Conversation,

        data: ConversationUpdate,

    ) -> Conversation:

        update_data = data.model_dump(

            exclude_unset=True

        )

        for key, value in update_data.items():

            setattr(

                conversation,

                key,

                value,

            )

        await conversation_repository.save(

            db=db,

            conversation=conversation,

        )

        await db.commit()

        await db.refresh(conversation)

        return conversation

    async def archive(

        self,

        db: AsyncSession,

        conversation: Conversation,

    ) -> Conversation:

        await conversation_repository.archive(

            db=db,

            conversation_id=conversation.id,

        )

        await db.commit()

        await db.refresh(conversation)

        return conversation

    async def delete(

        self,

        db: AsyncSession,

        conversation: Conversation,

    ):

        await conversation_repository.soft_delete(

            db=db,

            conversation_id=conversation.id,

        )

        await db.commit()


conversation_service = ConversationService()