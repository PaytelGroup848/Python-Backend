from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from app.db.database import Base


class AnalyticsLog(Base):

    __tablename__ = "analytics_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    session_id = Column(String)

    query = Column(String)

    rewritten_query = Column(String)

    response_time = Column(Float)

    retrieved_docs = Column(Integer)

    tool_used = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )