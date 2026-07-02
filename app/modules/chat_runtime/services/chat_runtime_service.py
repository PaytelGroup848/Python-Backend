from sqlalchemy.ext.asyncio import AsyncSession

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

        organization_id: int,

        workspace_id: int,

        user_id: int,

        request: ChatRequest,

    ) -> ChatResponse:

        return await chat_pipeline.execute(

            db=db,

            organization_id=organization_id,

            workspace_id=workspace_id,

            user_id=user_id,

            request=request,

        )


chat_runtime_service = ChatRuntimeService()