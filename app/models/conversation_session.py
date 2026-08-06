from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey

from sqlalchemy.orm import relationship

from datetime import datetime

from app.db.database import Base


class ConversationSession(Base):

    __tablename__ = "conversation_sessions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    title = Column(
        String,
        default="New Chat"
    )

    assistant_id = Column(
        Integer,
        ForeignKey("assistants.id", name="fk_conversation_sessions_assistant_id"),
        nullable=True,
        index=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete"
    )