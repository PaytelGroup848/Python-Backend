from fastapi import (
    APIRouter,
    Depends,
    Query,
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

from app.modules.chat.schemas.conversation_create import (
    ConversationCreate,
)

from app.modules.chat.schemas.conversation_update import (
    ConversationUpdate,
)

from app.modules.chat.schemas.conversation_response import (
    ConversationResponse,
)

from app.modules.chat.services.conversation_service import (
    conversation_service,
)

from app.modules.chat.dependencies.current_conversation import (
    get_current_conversation,
)

from app.modules.chat.models.conversation import (
    Conversation,
)


router = APIRouter(

    prefix="/conversations",

    tags=["Conversations"]

)

@router.post(

    "",

    response_model=ConversationResponse,

    status_code=status.HTTP_201_CREATED,

)
async def create_conversation(

    data: ConversationCreate,

    context: RequestContext = Depends(
        get_request_context
    ),

    db: AsyncSession = Depends(
        get_db
    ),

):

    return await conversation_service.create_conversation(

        db=db,

        context=context,

        data=data,

    )

@router.get(

    "",

    response_model=list[ConversationResponse],

)
async def list_conversations(

    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),

    cursor: int | None = Query(
        default=None,
    ),

    context: RequestContext = Depends(
        get_request_context
    ),

    db: AsyncSession = Depends(
        get_db
    ),

):

    return await conversation_service.list_workspace_conversations(

        db=db,

        organization_id=context.organization.id,

        workspace_id=context.workspace.id,

        limit=limit,

        cursor=cursor,

    )

@router.get(

    "/{conversation_id}",

    response_model=ConversationResponse,

)
async def get_conversation(

    conversation: Conversation = Depends(
        get_current_conversation
    ),

):

    return conversation

@router.patch(

    "/{conversation_id}",

    response_model=ConversationResponse,

)
async def update_conversation(

    data: ConversationUpdate,

    conversation: Conversation = Depends(
        get_current_conversation
    ),

    db: AsyncSession = Depends(
        get_db
    ),

):

    return await conversation_service.update_conversation(

        db=db,

        conversation=conversation,

        data=data,

    )

@router.patch(

    "/{conversation_id}/archive",

    response_model=ConversationResponse,

)
async def archive_conversation(

    conversation: Conversation = Depends(
        get_current_conversation
    ),

    db: AsyncSession = Depends(
        get_db
    ),

):

    return await conversation_service.archive(

        db=db,

        conversation=conversation,

    )

@router.delete(

    "/{conversation_id}",

    status_code=status.HTTP_204_NO_CONTENT,

)
async def delete_conversation(

    conversation: Conversation = Depends(
        get_current_conversation
    ),

    db: AsyncSession = Depends(
        get_db
    ),

):

    await conversation_service.delete(

        db=db,

        conversation=conversation,

    )