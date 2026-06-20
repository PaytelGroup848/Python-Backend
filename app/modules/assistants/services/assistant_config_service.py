from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.assistants.models.assistant_config import (
    AssistantConfig
)

from app.modules.assistants.repositories.assistant_config_repository import (
    assistant_config_repository
)


class AssistantConfigService:

    async def create_config(

        self,

        db: AsyncSession,

        data: dict
    ):

        config = AssistantConfig(
            **data
        )

        return await (
            assistant_config_repository
            .create(
                db,
                config
            )
        )

    async def get_config(

        self,

        db: AsyncSession,

        assistant_id: int
    ):

        return await (
            assistant_config_repository
            .get_by_assistant_id(
                db,
                assistant_id
            )
        )


assistant_config_service = (
    AssistantConfigService()
)