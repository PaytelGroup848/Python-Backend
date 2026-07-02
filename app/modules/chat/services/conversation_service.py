from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.chat.models.conversation import (
    Conversation
)

from app.modules.chat.repositories.conversation_repository import (
    conversation_repository
)

from app.modules.chat.schemas.conversation_create import (
    ConversationCreate
)

from app.modules.chat.schemas.conversation_update import (
    ConversationUpdate
)


class ConversationService:

    async def create_conversation(

        self,

        db: AsyncSession,

        organization_id: int,

        created_by: int,

        data: ConversationCreate

    ) -> Conversation:

        conversation = Conversation(

            organization_id=organization_id,

            workspace_id=data.workspace_id,

            assistant_id=data.assistant_id,

            created_by=created_by,

            title=data.title

        )

        conversation = await (

            conversation_repository.create(

                db=db,

                conversation=conversation

            )

        )

        await db.commit()

        await db.refresh(
            conversation
        )

        return conversation

    async def get_conversation(

        self,

        db: AsyncSession,

        conversation_id: int

    ):

        return await (

            conversation_repository.get_by_id(

                db=db,

                conversation_id=conversation_id

            )

        )

    async def list_workspace_conversations(

        self,

        db: AsyncSession,

        organization_id: int,

        workspace_id: int,

        limit: int = 20,

        offset: int = 0

    ):

        return await (

            conversation_repository.list_by_workspace(

                db=db,

                organization_id=organization_id,

                workspace_id=workspace_id,

                limit=limit,

                offset=offset

            )

        )

    async def update_conversation(

        self,

        db: AsyncSession,

        conversation: Conversation,

        data: ConversationUpdate

    ):

        update_data = data.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():

            setattr(
                conversation,
                key,
                value
            )

        await db.commit()

        await db.refresh(
            conversation
        )

        return conversation

    async def archive(

        self,

        db: AsyncSession,

        conversation_id: int

    ):

        await (

            conversation_repository.archive(

                db=db,

                conversation_id=conversation_id

            )

        )

        await db.commit()

    async def delete(

        self,

        db: AsyncSession,

        conversation_id: int

    ):

        await (

            conversation_repository.soft_delete(

                db=db,

                conversation_id=conversation_id

            )

        )

        await db.commit()


conversation_service = (
    ConversationService()
)