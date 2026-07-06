from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)

from sqlalchemy.dialects.postgresql import JSONB

from app.db.database import Base


class StorageImplementation(Base):

    __tablename__ = "storage_implementations"

    __table_args__ = (
        UniqueConstraint(
            "implementation_code",
            "implementation_version",
            name="uq_storage_implementation_code_version",
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    implementation_code = Column(
        String(150),
        nullable=False,
        index=True,
    )

    implementation_version = Column(
        String(100),
        nullable=False,
    )

    display_name = Column(
        String(255),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    runtime_type = Column(
        String(100),
        nullable=False,
        index=True,
    )

    configuration_schema_json = Column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    capabilities_json = Column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        index=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
        onupdate=datetime.utcnow,
    )