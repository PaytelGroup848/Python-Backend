from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey

from app.db.database import Base


class GeneratedImage(Base):
    __tablename__ = "generated_images"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id = Column(Integer, ForeignKey("conversation_sessions.id", ondelete="CASCADE"), nullable=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="SET NULL"), nullable=True, index=True)

    provider = Column(String(50), nullable=False)
    model_name = Column(String(100), nullable=False)
    original_prompt = Column(Text, nullable=False)
    enhanced_prompt = Column(Text, nullable=False)
    file_path = Column(String(500), nullable=False)
    file_url = Column(String(500), nullable=False)
    parent_image_id = Column(Integer, ForeignKey("generated_images.id", ondelete="SET NULL"), nullable=True, index=True)
    edit_type = Column(String(50), default="generation")
    mime_type = Column(String(50), default="image/png")
    aspect_ratio = Column(String(20), default="1024x1024")
    status = Column(String(20), default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)
