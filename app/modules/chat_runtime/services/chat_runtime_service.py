from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.shared.context.request_context import (
    RequestContext,
)

from app.modules.chat_runtime.manager.chat_pipeline import (
    chat_pipeline,
)

from app.modules.chat_runtime.schemas.chat_request import (
    ChatRequest,
)

from app.modules.chat_runtime.schemas.chat_response import (
    ChatResponse,
)


class ChatRuntimeService:

    async def send_message(

        self,

        db: AsyncSession,

        context: RequestContext,

        request: ChatRequest,

    ) -> ChatResponse:

        return await chat_pipeline.execute(

            db=db,

            context=context,

            request=request,

        )


chat_runtime_service = ChatRuntimeService()