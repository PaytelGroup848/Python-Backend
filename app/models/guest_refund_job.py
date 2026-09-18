from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.db.database import Base


class GuestRefundJob(Base):
    __tablename__ = "guest_refund_jobs"

    id = Column(Integer, primary_key=True, index=True)
    guest_user_id = Column(Integer, nullable=False, index=True)
    request_id = Column(String(64), unique=True, nullable=False, index=True)
    reason = Column(String(255), nullable=True)
    status = Column(String(20), nullable=False, default="PENDING", index=True)  # PENDING, PROCESSING, COMPLETED, FAILED
    attempt_count = Column(Integer, nullable=False, default=0)
    next_attempt_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    last_error = Column(Text, nullable=True)
    locked_at = Column(DateTime, nullable=True)
    locked_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
