from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
    DateTime,
    Boolean
)

from sqlalchemy.sql import func

from pgvector.sqlalchemy import Vector

from app.db.database import Base


class Document(Base):

    __tablename__ = "documents"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # -----------------------------
    # TRANSLATED / SEARCHABLE TEXT
    # -----------------------------

    content = Column(
        Text,
        nullable=False
    )

    # -----------------------------
    # ORIGINAL PDF TEXT
    # -----------------------------

    original_content = Column(
        Text,
        nullable=True
    )

    # -----------------------------
    # DETECTED LANGUAGE
    # -----------------------------

    language = Column(
        String,
        default="en"
    )

    # -----------------------------
    # TRANSLATION STATUS
    # -----------------------------

    is_translated = Column(
        Boolean,
        default=False
    )

    # -----------------------------
    # VECTOR EMBEDDING
    # -----------------------------

    embedding = Column(
        Vector(384)
    )

    source_file = Column(
        String,
        nullable=True
    )

    page_number = Column(
        Integer,
        nullable=True
    )

    department = Column(
        String,
        nullable=True
    )

    access_level = Column(
        String,
        nullable=True
    )

    uploaded_by = Column(
        Integer,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )