from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
    DateTime
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

    content = Column(
        Text,
        nullable=False
    )

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