from fastapi import (
    APIRouter,
    Depends,
    status,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.db.database import (
    get_db,
)

from app.shared.context.request_context import (
    RequestContext,
)

from app.modules.auth.dependencies.current_request_context import (
    get_request_context,
)

from app.modules.chat_runtime.schemas.chat_request import (
    ChatRequest,
)

from app.modules.chat_runtime.schemas.chat_response import (
    ChatResponse,
)

from app.modules.chat_runtime.services.chat_runtime_service import (
    chat_runtime_service,
)


router = APIRouter(

    prefix="/chat",

    tags=["Chat"],

)


@router.post(

    "",

    response_model=ChatResponse,

    status_code=status.HTTP_200_OK,

)
async def send_message(

    request: ChatRequest,

    context: RequestContext = Depends(
        get_request_context
    ),

    db: AsyncSession = Depends(
        get_db
    ),

) -> ChatResponse:

    return await (

        chat_runtime_service.send_message(

            db=db,

            context=context,

            request=request,

        )

    )