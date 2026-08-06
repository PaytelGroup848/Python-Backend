from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    func,
    UniqueConstraint
)

from app.db.database import Base


class ModelVersion(Base):

    __tablename__ = "model_versions"

    __table_args__ = (

        UniqueConstraint(

            "model_id",

            "version",

            name="uq_model_versions_model_version"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    model_id = Column(
        Integer,
        ForeignKey("models.id"),
        nullable=False,
        index=True
    )

    training_job_id = Column(
        Integer,
        ForeignKey(
            "training_jobs.id",
            name="fk_model_version_training_job_id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    artifact_id = Column(
        Integer,
        ForeignKey(
            "model_artifacts.id",
            name="fk_model_version_artifact_id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    version = Column(
        String(100),
        nullable=False,
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

    status = Column(
        String(50),
        nullable=False,
        default="CREATED",
        server_default="CREATED",
        index=True,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    is_release_ready = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    is_deployment_ready = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    source_type = Column(
        String(50),
        nullable=True,
        index=True
    )

    source_uri = Column(
        String(1000),
        nullable=True
    )

    source_revision = Column(
        String(255),
        nullable=True
    )

    parent_model_version_id = Column(
        Integer,
        ForeignKey(
            "model_versions.id",
            name="fk_model_version_parent_id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        server_default=func.now(),
        onupdate=datetime.utcnow,
        nullable=False,
    )