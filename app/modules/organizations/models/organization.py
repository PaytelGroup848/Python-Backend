from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
    func
)

from app.db.database import Base

from app.shared.constants.organization_status import (
    OrganizationStatus
)

from app.shared.constants.organization_type import (
    OrganizationType
)


class Organization(Base):

    __tablename__ = "organizations"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    code = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True
    )

    name = Column(
        String(255),
        nullable=False
    )

    slug = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True
    )

    description = Column(
        Text,
        nullable=True
    )

    logo_url = Column(
        String(1000),
        nullable=True
    )

    website = Column(
        String(500),
        nullable=True
    )

    email = Column(
        String(255),
        nullable=True
    )

    phone = Column(
        String(50),
        nullable=True
    )

    country = Column(
        String(100),
        nullable=True
    )

    timezone = Column(
        String(100),
        nullable=True
    )

    organization_type = Column(
        String(50),
        nullable=False,
        default=OrganizationType.PERSONAL.value,
        server_default=OrganizationType.PERSONAL.value,
        index=True
    )

    status = Column(
        String(50),
        nullable=False,
        default=OrganizationStatus.ACTIVE.value,
        server_default=OrganizationStatus.ACTIVE.value,
        index=True
    )

    is_system = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false"
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true"
    )

    created_by = Column(
        String(255),
        nullable=True
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
        onupdate=datetime.utcnow
    )