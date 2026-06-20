from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.assistants.repositories.assistant_repository import (
    assistant_repository
)

from app.modules.assistants.repositories.assistant_knowledge_base_repository import (
    assistant_knowledge_base_repository
)

from app.modules.assistants.schemas.assistant_runtime_schema import (
    AssistantRuntime
)

from app.modules.assistants.services.assistant_config_service import (
    assistant_config_service
)

from app.modules.models.services.model_runtime_service import (
    model_runtime_service
)


class AssistantRuntimeService:

    async def load_runtime(

        self,

        db: AsyncSession,

        assistant_id: int

    ) -> AssistantRuntime:

        assistant = await (
            assistant_repository
            .get_by_id(
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

        config = await (
            assistant_config_service
            .get_config(
                db=db,
                assistant_id=assistant_id
            )
        )

        model_runtime = await (
            model_runtime_service
            .load_runtime(
            db=db,
            assistant_id=assistant_id
        )
        
    )

        return AssistantRuntime(

            assistant_id=
                assistant.id,

            assistant_name=
                assistant.name,

            assistant_code=
                assistant.code,

            system_prompt=
                assistant.system_prompt,

            knowledge_base_ids=
                knowledge_base_ids,

            provider_id=
                model_runtime.provider_id
                if model_runtime
                else None,

            model_id=
                model_runtime.model_id
                if model_runtime
                else None,

            model_version_id=
                model_runtime.model_version_id
                if model_runtime
                else None,

            model_code=
                model_runtime.model_code
                if model_runtime
                else None,

            model_display_name=
                model_runtime.model_display_name
                if model_runtime
                else None,

            version=
                model_runtime.version
                if model_runtime
                else None,

            version_display_name=
                model_runtime.version_display_name
                if model_runtime
                else None,

            temperature=
                config.temperature
                if config
                else 0.2,

            top_p=
                config.top_p
                if config
                else 0.95,

            max_tokens=
                config.max_tokens
                if config
                else 4000,

            context_window=
                config.context_window
                if config
                else 8000,

            memory_enabled=
                config.memory_enabled
                if config
                else True,

            rag_enabled=
                config.rag_enabled
                if config
                else True,

            cag_enabled=
                config.cag_enabled
                if config
                else False,

            tool_calling_enabled=
                config.tool_calling_enabled
                if config
                else False
       )


assistant_runtime_service = (
    AssistantRuntimeService()
)