from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.assistants.repositories.assistant_repository import (
    assistant_repository
)

from app.modules.assistants.repositories.assistant_knowledge_base_repository import (
    assistant_knowledge_base_repository
)


class AssistantResolverService:

    async def resolve_assistant(

        self,

        db: AsyncSession,

        assistant_id: int
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

        mappings = await (
            assistant_knowledge_base_repository
            .list_by_assistant(
                db,
                assistant_id
            )
        )

        knowledge_base_ids = [

            mapping.knowledge_base_id

            for mapping in mappings
        ]

        if not knowledge_base_ids:

            raise ValueError(
                "No knowledge base linked to assistant"
            )

        return {

            "assistant_id":
            assistant.id,

            "assistant_name":
            assistant.name,

            "assistant_code":
            assistant.code,

            "knowledge_base_ids":
            knowledge_base_ids
        }


assistant_resolver_service = (
    AssistantResolverService()
)