from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
)

from sqlalchemy.dialects.postgresql import JSONB

from app.db.database import Base


class ConnectorInstance(Base):

    __tablename__ = "connector_instances"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    connector_implementation_id = Column(
        Integer,
        ForeignKey(
            "connector_implementations.id",
            name="fk_connector_instance_impl_id"
        ),
        nullable=False,
        index=True
    )

    organization_id = Column(
        Integer,
        nullable=True,
        index=True
    )

    name = Column(
        String(255),
        nullable=False
    )

    instance_code = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True
    )

    description = Column(
        String,
        nullable=True
    )

    status = Column(
        String(50),
        nullable=False,
        index=True
    )

    configuration_json = Column(
        JSONB,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )