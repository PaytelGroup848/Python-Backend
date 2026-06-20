from sqlalchemy import select

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from app.modules.assistants.models.assistant_config import (
    AssistantConfig
)


class AssistantConfigRepository:

    async def create(

        self,

        db: AsyncSession,

        config: AssistantConfig
    ):

        db.add(config)

        await db.flush()

        await db.refresh(
            config
        )

        return config

    async def get_by_assistant_id(

        self,

        db: AsyncSession,

        assistant_id: int
    ):

        result = await db.execute(

            select(
                AssistantConfig
            ).where(

                AssistantConfig.assistant_id
                ==
                assistant_id
            )
        )

        return (
            result.scalar_one_or_none()
        )

    async def update(

        self,

        db: AsyncSession,

        config: AssistantConfig
    ):

        await db.flush()

        await db.refresh(
            config
        )

        return config


assistant_config_repository = (
    AssistantConfigRepository()
)