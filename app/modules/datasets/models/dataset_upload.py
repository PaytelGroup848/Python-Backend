from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)

from sqlalchemy.dialects.postgresql import (
    JSONB,
)

from sqlalchemy.orm import (
    relationship,
)

from app.db.database import Base


class DatasetUpload(Base):

    __tablename__ = "dataset_uploads"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    dataset_id = Column(
        Integer,
        ForeignKey(
            "datasets.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    original_file_name = Column(
        String(500),
        nullable=False,
    )

    stored_file_name = Column(
        String(500),
        nullable=False,
        unique=True,
    )

    file_extension = Column(
        String(30),
        nullable=False,
    )

    mime_type = Column(
        String(255),
        nullable=False,
    )

    file_size = Column(
        BigInteger,
        nullable=False,
    )

    storage_provider = Column(
        String(100),
        nullable=False,
    )

    storage_reference = Column(
        Text,
        nullable=False,
    )

    checksum = Column(
        String(128),
        nullable=True,
    )

    upload_status = Column(
        String(50),
        nullable=False,
        default="UPLOADED",
    )

    ingestion_status = Column(
        String(50),
        nullable=False,
        default="PENDING",
    )

    parser_type = Column(
        String(100),
        nullable=True,
    )

    parser_version = Column(
        String(100),
        nullable=True,
    )

    metadata_json = Column(
        JSONB,
        nullable=True,
    )

    error_message = Column(
        Text,
        nullable=True,
    )

    created_by = Column(
        String(255),
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    dataset = relationship(
        "Dataset",
        back_populates="uploads",
    )