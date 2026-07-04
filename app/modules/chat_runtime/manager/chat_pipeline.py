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

from app.modules.conversation_runtime.services.conversation_runtime_service import (
    conversation_runtime_service,
)

from app.modules.workspace_runtime.services.workspace_runtime_service import (
    workspace_runtime_service,
)

from app.modules.model_runtime.services.model_runtime_service import (
    model_runtime_service,
)

from app.modules.inference_runtime.services.inference_service import (
    inference_service,
)
from app.shared.context.request_context import (
    RequestContext
)

from app.modules.inference_runtime.schemas.inference_request import (
    InferenceRequest
)

class ChatPipeline:

    async def execute(

        self,

        db: AsyncSession,

        context: RequestContext,

        request: ChatRequest,

    ) -> ChatResponse:

        #
        # STEP 1
        # Save User Message
        #

        await chat_message_service.create_user_message(

            db=db,

            organization_id=context.organization.id,

            workspace_id=context.workspace.id,

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

        conversation_context = await (

            conversation_runtime_service.prepare_context(

                db=db,

                conversation_id=request.conversation_id,

            )

        )

        #
        # STEP 3
        # Resolve Workspace Runtime
        #

        workspace_runtime = await (

            workspace_runtime_service.load_runtime(

                db=db,

                workspace_id=context.workspace.id,

            )

        )

        #
        # STEP 4
        # Resolve Model Runtime
        #

        model_runtime = await (

            model_runtime_service.load_runtime(

                db=db,

                workspace_runtime=workspace_runtime,

            )

        )

        #
        # STEP 5
        # Execute Inference
        #

        inference_result = await (

            inference_service.generate(

                runtime=model_runtime,

                request=InferenceRequest(

                    context=conversation_context,

                ),

            )

        )

        #
        # STEP 6
        # Save Assistant Message
        #

        await chat_message_service.create_assistant_message(

            db=db,

            organization_id=context.organization.id,

            workspace_id=context.workspace.id,

            conversation_id=request.conversation_id,

            content=inference_result.text,

            model_release_id=model_runtime.release_id,

            input_tokens=inference_result.prompt_tokens,

            output_tokens=inference_result.generated_tokens,

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

            response=inference_result.text,

        )


chat_pipeline = ChatPipeline()