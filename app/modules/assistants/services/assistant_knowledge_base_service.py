from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assistant_knowledge_base import (
    AssistantKnowledgeBase
)

from app.modules.assistants.repositories.assistant_repository import (
    assistant_repository
)

from app.modules.assistants.repositories.assistant_knowledge_base_repository import (
    assistant_knowledge_base_repository
)

from app.modules.knowledge_bases.repositories.knowledge_base_repository import (
    knowledge_base_repository
)


class AssistantKnowledgeBaseService:

    async def create_mapping(
        self,
        db: AsyncSession,
        assistant_id: int,
        knowledge_base_id: int
    ):

        assistant = await (
            assistant_repository.get_by_id(
                db,
                assistant_id
            )
        )

        if not assistant:

            raise ValueError(
                "Assistant not found"
            )

        knowledge_base = await (
            knowledge_base_repository.get_by_id(
                db,
                knowledge_base_id
            )
        )

        if not knowledge_base:

            raise ValueError(
                "Knowledge base not found"
            )

        existing_mapping = await (
            assistant_knowledge_base_repository
            .get_mapping(
                db,
                assistant_id,
                knowledge_base_id
            )
        )

        if existing_mapping:

            raise ValueError(
                "Mapping already exists"
            )

        mapping = (
            AssistantKnowledgeBase(

                assistant_id=
                assistant_id,

                knowledge_base_id=
                knowledge_base_id,

                is_active=True
            )
        )

        return await (
            assistant_knowledge_base_repository
            .create(
                db,
                mapping
            )
        )

    async def list_assistant_knowledge_bases(
        self,
        db: AsyncSession,
        assistant_id: int
    ):

        return await (
            assistant_knowledge_base_repository
            .list_by_assistant(
                db,
                assistant_id
            )
        )

    async def list_knowledge_base_assistants(
        self,
        db: AsyncSession,
        knowledge_base_id: int
    ):

        return await (
            assistant_knowledge_base_repository
            .list_by_knowledge_base(
                db,
                knowledge_base_id
            )
        )

    async def deactivate_mapping(
        self,
        db: AsyncSession,
        assistant_id: int,
        knowledge_base_id: int
    ):

        mapping = await (
            assistant_knowledge_base_repository
            .get_mapping(
                db,
                assistant_id,
                knowledge_base_id
            )
        )

        if not mapping:

            raise ValueError(
                "Mapping not found"
            )

        mapping.is_active = False

        return await (
            assistant_knowledge_base_repository
            .update(
                db,
                mapping
            )
        )


assistant_knowledge_base_service = (
    AssistantKnowledgeBaseService()
)