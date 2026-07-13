from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.assistants.services.assistant_runtime_service import (
    assistant_runtime_service,
)


class AssistantResolverService:

    async def resolve_assistant(

        self,

        db: AsyncSession,

        assistant_id: int,

    ):

        return await (

            assistant_runtime_service

            .load_runtime(

                db=db,

                assistant_id=assistant_id,

            )

        )


assistant_resolver_service = (
    AssistantResolverService()
)