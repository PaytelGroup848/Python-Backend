from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db.database import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer)

    refresh_token = Column(String, unique=True)

    created_at = Column(DateTime, default=datetime.utcnow)