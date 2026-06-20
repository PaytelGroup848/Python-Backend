from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey
)

from app.db.database import Base


class ModelDeployment(Base):

    __tablename__ = "model_deployments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    model_version_id = Column(
        Integer,
        ForeignKey(
            "model_versions.id"
        ),
        nullable=False,
        index=True
    )

    deployment_name = Column(
        String(255),
        nullable=False
    )

    deployment_type = Column(
        String(100),
        nullable=False
    )

    endpoint_url = Column(
        String(500),
        nullable=False
    )

    max_context_window = Column(
        Integer,
        nullable=False,
        default=8192
    )

    gpu_type = Column(
        String(100),
        nullable=True
    )

    gpu_count = Column(
        Integer,
        nullable=True
    )

    is_active = Column(
        Boolean,
        default=True,
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