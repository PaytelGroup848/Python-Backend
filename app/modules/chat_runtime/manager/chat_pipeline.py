from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.chat.schemas.chat_message_create import (
    ChatMessageCreate,
)

from app.modules.chat_runtime.schemas.chat_request import (
    ChatRequest,
)

from app.modules.chat_runtime.schemas.chat_response import (
    ChatResponse,
)

from app.modules.chat.services.chat_message_service import (
    chat_message_service,
)

from app.modules.conversation_runtime.manager.conversation_runtime_manager import (
    conversation_runtime_manager,
)

from app.modules.workspace_runtime.manager.workspace_runtime_manager import (
    workspace_runtime_manager,
)

from app.modules.model_runtime.manager.model_runtime_manager import (
    model_runtime_manager,
)

from app.modules.inference_runtime.manager.inference_manager import (
    inference_manager,
)


class ChatPipeline:

    async def execute(

        self,

        db: AsyncSession,

        organization_id: int,

        workspace_id: int,

        user_id: int,

        request: ChatRequest,

    ) -> ChatResponse:

        #
        # STEP 1
        # Save User Message
        #

        await chat_message_service.create_user_message(

            db=db,

            organization_id=organization_id,

            workspace_id=workspace_id,

            data=ChatMessageCreate(

                conversation_id=request.conversation_id,

                content=request.message,

            ),

        )

        #
        # Commit user message before inference
        #

        await db.commit()

        #
        # STEP 2
        # Build Conversation Context
        #

        conversation_context = (

            await conversation_runtime_manager.prepare_context(

                db=db,

                conversation_id=request.conversation_id,

            )

        )

        #
        # STEP 3
        # Resolve Workspace Runtime
        #

        workspace_runtime = (

            await workspace_runtime_manager.resolve_runtime(

                db=db,

                workspace_id=workspace_id,

            )

        )

        #
        # STEP 4
        # Resolve Model Runtime
        #

        model_runtime = (

            await model_runtime_manager.load_runtime(

                db=db,

                workspace_runtime=workspace_runtime,

            )

        )

        #
        # STEP 5
        # Execute Inference
        #

        inference_result = (

            await inference_manager.generate(

                runtime=model_runtime,

                context=conversation_context,

            )

        )

        #
        # STEP 6
        # Save Assistant Message
        #

        await chat_message_service.create_assistant_message(

            db=db,

            organization_id=organization_id,

            workspace_id=workspace_id,

            conversation_id=request.conversation_id,

            content=inference_result.response,

            model_release_id=inference_result.model_release_id,

            input_tokens=inference_result.input_tokens,

            output_tokens=inference_result.output_tokens,

            latency_ms=inference_result.latency_ms,

            finish_reason=inference_result.finish_reason,

        )

        await db.commit()

        #
        # STEP 7
        # Return
        #

        return ChatResponse(

            conversation_id=request.conversation_id,

            response=inference_result.response,

        )


chat_pipeline = ChatPipeline()