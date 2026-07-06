from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
    text,
)

from sqlalchemy.dialects.postgresql import JSONB

from app.db.database import Base

from app.shared.constants.storage_scope_type import (
    StorageScopeType,
)


class StorageInstance(Base):

    __tablename__ = "storage_instances"

    __table_args__ = (

        CheckConstraint(
            "("
            "scope_type = 'PLATFORM' "
            "AND organization_id IS NULL "
            "AND workspace_id IS NULL"
            ") OR ("
            "scope_type = 'ORGANIZATION' "
            "AND organization_id IS NOT NULL "
            "AND workspace_id IS NULL"
            ") OR ("
            "scope_type = 'WORKSPACE' "
            "AND organization_id IS NOT NULL "
            "AND workspace_id IS NOT NULL"
            ")",
            name="ck_storage_instance_scope_identity",
        ),

        Index(
            "uq_storage_instance_platform_code",
            "instance_code",
            unique=True,
            postgresql_where=text(
                "scope_type = 'PLATFORM'"
            ),
        ),

        Index(
            "uq_storage_instance_organization_code",
            "organization_id",
            "instance_code",
            unique=True,
            postgresql_where=text(
                "scope_type = 'ORGANIZATION'"
            ),
        ),

        Index(
            "uq_storage_instance_workspace_code",
            "workspace_id",
            "instance_code",
            unique=True,
            postgresql_where=text(
                "scope_type = 'WORKSPACE'"
            ),
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    storage_implementation_id = Column(
        Integer,
        ForeignKey(
            "storage_implementations.id",
            name="fk_storage_instance_implementation_id",
        ),
        nullable=False,
        index=True,
    )

    scope_type = Column(
        String(50),
        nullable=False,
        default=StorageScopeType.PLATFORM.value,
        server_default=StorageScopeType.PLATFORM.value,
        index=True,
    )

    organization_id = Column(
        Integer,
        ForeignKey(
            "organizations.id",
            name="fk_storage_instance_organization_id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    workspace_id = Column(
        Integer,
        ForeignKey(
            "workspaces.id",
            name="fk_storage_instance_workspace_id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    instance_code = Column(
        String(150),
        nullable=False,
        index=True,
    )

    display_name = Column(
        String(255),
        nullable=False,
    )

    configuration_json = Column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    secret_reference = Column(
        String(1000),
        nullable=True,
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