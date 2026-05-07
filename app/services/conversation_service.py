from app.db.database import SessionLocal
from app.models.conversation import Conversation
import uuid

def save_conversation(user_id, query, response, model_used):
    db = SessionLocal()

    convo = Conversation(
        user_id=user_id,
        session_id=str(uuid.uuid4()),
        query=query,
        response=response,
        model_used=model_used
    )

    db.add(convo)
    db.commit()
    db.close()