from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assistant_model_version import (
    AssistantModelVersion
)

from app.models.model_version import (
    ModelVersion
)

from app.models.model import (
    ModelRegistry
)


class ModelVersionRepository:

    async def get_runtime_by_assistant(
        self,
        db: AsyncSession,
        assistant_id: int
    ):

        stmt = (

            select(

                AssistantModelVersion,

                ModelVersion,

                ModelRegistry

            )

            .join(

                ModelVersion,

                AssistantModelVersion
                .model_version_id
                ==
                ModelVersion.id
            )

            .join(

                ModelRegistry,

                ModelVersion.model_id
                ==
                ModelRegistry.id
            )

            .where(

                AssistantModelVersion
                .assistant_id
                ==
                assistant_id,

                AssistantModelVersion
                .is_active
                ==
                True,

                AssistantModelVersion
                .is_default
                ==
                True
            )
        )

        result = await db.execute(
            stmt
        )

        return result.first()


model_version_repository = (
    ModelVersionRepository()
)