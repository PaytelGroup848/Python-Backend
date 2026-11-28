from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class GeneratedImage(Base):
    __tablename__ = "generated_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("conversation_sessions.id", ondelete="CASCADE"), nullable=True, index=True)
    message_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("messages.id", ondelete="SET NULL"), nullable=True, index=True)

    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    original_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    enhanced_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    parent_image_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("generated_images.id", ondelete="SET NULL"), nullable=True, index=True)
    edit_type: Mapped[Optional[str]] = mapped_column(String(50), default="generation")
    mime_type: Mapped[Optional[str]] = mapped_column(String(50), default="image/png")
    aspect_ratio: Mapped[Optional[str]] = mapped_column(String(20), default="1024x1024")
    status: Mapped[Optional[str]] = mapped_column(String(20), default="completed")
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow)
