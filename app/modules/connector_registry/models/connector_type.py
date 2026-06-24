from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime
)

from app.db.database import Base


class ConnectorType(Base):

    __tablename__ = "connector_types"

    id = Column(
        Integer,
        primary_key=True
    )

    code = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True
    )

    display_name = Column(
        String(255),
        nullable=False
    )

    description = Column(
        String,
        nullable=True
    )

    is_active = Column(
        Boolean,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )