from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
    UniqueConstraint
)

from app.db.database import Base


class Workspace(Base):

    __tablename__ = "workspaces"

    __table_args__ = (

        UniqueConstraint(

            "organization_id",

            "code",

            name="uq_workspace_organization_code"

        ),

        UniqueConstraint(

            "organization_id",

            "slug",

            name="uq_workspace_organization_slug"

        ),

    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    organization_id = Column(
        Integer,
        ForeignKey(
            "organizations.id",
            name="fk_workspace_organization_id"
        ),
        nullable=False,
        index=True
    )

    code = Column(
        String(100),
        nullable=False,
        index=True
    )

    name = Column(
        String(255),
        nullable=False
    )

    slug = Column(
        String(255),
        nullable=False,
        index=True
    )

    description = Column(
        Text,
        nullable=True
    )

    icon_url = Column(
        String(1000),
        nullable=True
    )

    is_system = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false"
    )

    is_public = Column(
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

    created_by_user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            name="fk_workspace_created_by_user_id"
        ),
        nullable=False,
        index=True
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