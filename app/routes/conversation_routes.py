from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from sqlalchemy import select

from app.models.message import (
    Message,
)

from app.schemas.message import (
    MessageResponse,
)

from app.db.database import (
    get_db,
)

from app.models.conversation_session import (
    ConversationSession,
)

from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
)

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)

# =========================
# CREATE CONVERSATION
# =========================

@router.post(
    "",
    response_model=ConversationResponse
)
async def create_conversation(
    payload: ConversationCreate,
    db: AsyncSession = Depends(get_db),
):

    conversation = ConversationSession(
        user_id=1,
        title=payload.title,
    )

    db.add(conversation)

    await db.commit()

    await db.refresh(conversation)

    return conversation


# =========================
# GET CONVERSATIONS
# =========================

@router.get(
    "",
    response_model=list[
        ConversationResponse
    ]
)
async def get_conversations(
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(

        select(
            ConversationSession
        )
        .where(
            ConversationSession.user_id
            == 1
        )
        .order_by(
            ConversationSession.created_at.desc()
        )
    )

    conversations = (
        result.scalars().all()
    )

    return conversations

# =========================
# GET CONVERSATION MESSAGES
# =========================

@router.get(
    "/{conversation_id}/messages",
    response_model=list[
        MessageResponse
    ]
)
async def get_conversation_messages(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(

        select(Message)

        .where(
            Message.conversation_id
            == conversation_id
        )

        .order_by(
            Message.created_at.asc()
        )
    )

    messages = (
        result.scalars().all()
    )

    return messages