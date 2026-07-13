from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.modules.chat.services.chat_message_service import (
    chat_message_service,
)

from app.modules.chat.schemas.chat_message_create import (
    ChatMessageCreate,
)

from app.modules.conversation_runtime.services.conversation_runtime_service import (
    conversation_runtime_service,
)

from app.modules.workspace_runtime.services.workspace_runtime_service import (
    workspace_runtime_service,
)

from app.modules.assistants.services.assistant_runtime_service import (
    assistant_runtime_service,
)

from app.modules.conversation_execution_runtime.manager.conversation_execution_runtime_manager import (
    conversation_execution_runtime_manager,
)

from app.modules.models.services.model_inference_service import (
    model_inference_service,
)

from app.modules.models.schemas.model_generation_request import (
    ModelGenerationRequest,
)

class ConversationExecutionService:
    async def execute(

        self,

        db: AsyncSession,

        organization_id: int,

        workspace_id: int,

        conversation_id: int,

        content: str,

    ):
        
        user_message = await (

            chat_message_service

            .create_user_message(

                db=db,

                organization_id=organization_id,

                workspace_id=workspace_id,

                data=ChatMessageCreate(

                    conversation_id=conversation_id,

                    content=content,

                ),

            )

        )

        conversation_runtime = await (

            conversation_runtime_service

            .prepare_context(

                db=db,

                conversation_id=conversation_id,

            )

        )

        workspace_runtime = await (

            workspace_runtime_service

            .load_runtime(

                db=db,

                workspace_id=workspace_id,

            )

        )

        assistant_runtime = await (

            assistant_runtime_service

            .load_runtime(

                db=db,

                assistant_id=workspace_runtime.assistant_id,

            )

        )

        execution_context = await (

            conversation_execution_runtime_manager

            .resolve(

                db=db,

                conversation=conversation_runtime,

                workspace=workspace_runtime,

            )

        )

        if assistant_runtime.model_version_id is None:

            raise ValueError(
                "Assistant model version is not configured."
            )

        if execution_context.inference is None:

            raise ValueError(
                "Inference runtime not found."
            )

        generation_request = ModelGenerationRequest(

            prompt=content,

            temperature=
                assistant_runtime.temperature,

            max_tokens=
                assistant_runtime.max_tokens,

        )

        generation = await (

            model_inference_service

            .generate(

                db=db,

                model_version_id=
                    assistant_runtime.model_version_id,

                request=
                    generation_request,

            )

        )

        assistant_message = await (

            chat_message_service

            .create_assistant_message(

                db=db,

                organization_id=organization_id,

                workspace_id=workspace_id,

                conversation_id=conversation_id,

                content=generation.text,

            )

        )

        await db.commit()

        return {

            "conversation_id":
                conversation_id,

            "user_message":
                user_message,

            "assistant_message":
                assistant_message,

            "response":
                generation,

        }
    
conversation_execution_service = (
    ConversationExecutionService()
)
