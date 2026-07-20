from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint
)

from app.db.database import Base
from sqlalchemy.dialects.postgresql import JSONB


class ConnectorImplementation(Base):

    __tablename__ = "connector_implementations"

    __table_args__ = (
        UniqueConstraint(
            "implementation_code",
            "version",
            name="uq_connector_impl_version"
        ),
    )


    id = Column(
        Integer,
        primary_key=True
    )

    connector_type_id = Column(
        Integer,
        ForeignKey(
            "connector_types.id",
            name="fk_connector_impl_type_id"
        ),
        nullable=False,
        index=True
    )

    implementation_code = Column(
        String(100),
        nullable=False,
        index=True
    )

    version = Column(
        String(100),
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False,
        index=True
    )

    configuration_schema = Column(
        JSONB,
        nullable=True
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