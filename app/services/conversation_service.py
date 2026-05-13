import uuid

from app.db.database import AsyncSessionLocal
from app.models.conversation import Conversation


async def save_conversation(
    user_id,
    query,
    response,
    model_used
):

    async with AsyncSessionLocal() as db:

        convo = Conversation(
            user_id=user_id,
            session_id=str(uuid.uuid4()),
            query=query,
            response=response,
            model_used=model_used
        )

        db.add(convo)

        await db.commit()

        await db.refresh(convo)

        return convo