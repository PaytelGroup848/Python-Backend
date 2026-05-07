from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.db.database import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer)

    session_id = Column(String, index=True)

    query = Column(Text)

    response = Column(Text)

    model_used = Column(String)

    timestamp = Column(DateTime, default=datetime.utcnow)