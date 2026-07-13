from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)

from app.db.database import Base


class TrainingJob(Base):

    __tablename__ = "training_jobs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    dataset_id = Column(
        Integer,
        ForeignKey(
            "datasets.id",
            name="fk_training_job_dataset_id"
        ),
        nullable=False,
        index=True
    )

    dataset_snapshot_id = Column(
        Integer,
        ForeignKey(
            "dataset_snapshots.id",
            name=(
                "fk_training_job_"
                "dataset_snapshot_id"
            ),
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    training_provider_id = Column(
        Integer,
        ForeignKey(
            "training_providers.id",
            name="fk_training_job_provider_id"
        ),
        nullable=False,
        index=True
    )

    training_configuration_id = Column(
        Integer,
        ForeignKey(
            "training_configurations.id",
            name=(
                "fk_training_job_"
                "training_configuration_id"
            ),
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    base_model_id = Column(
        Integer,
        ForeignKey(
            "models.id",
            name="fk_training_job_base_model_id"
        ),
        nullable=False,
        index=True
    )

    base_model_version_id = Column(
        Integer,
        ForeignKey(
            "model_versions.id",
            name="fk_training_job_base_model_version_id",
            ondelete="RESTRICT"
        ),
        nullable=True,
        index=True
    )

    tokenizer_version_id = Column(
        Integer,
        ForeignKey(
            "tokenizer_versions.id",
            name=(
                "fk_training_job_"
                "tokenizer_version_id"
            ),
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    training_type = Column(
        String(100),
        nullable=False
    )

    priority = Column(
        Integer,
        nullable=False,
        default=100,
        server_default="100"
    )

    created_by = Column(
        String(255),
        nullable=True
    )

    status = Column(
        String(50),
        nullable=False,
        default="PENDING",
        server_default="PENDING",
        index=True
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true"
    )

    artifact_path = Column(
        String(1000),
        nullable=True
    )

    started_at = Column(
        DateTime,
        nullable=True
    )

    completed_at = Column(
        DateTime,
        nullable=True
    )

    queued_at = Column(
        DateTime,
        nullable=True,
    )

    failed_at = Column(
        DateTime,
        nullable=True,
    )

    failure_reason = Column(
        String(4000),
        nullable=True,
    )

    current_epoch = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    current_step = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    global_step = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    processed_samples = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    processed_tokens = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    current_loss = Column(
        Numeric(18, 8),
        nullable=True,
    )

    learning_rate = Column(
        Numeric(18, 12),
        nullable=True,
    )

    last_checkpoint_path = Column(
        String(1000),
        nullable=True,
    )

    last_checkpoint_at = Column(
        DateTime,
        nullable=True,
    )



    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        server_default=func.now(),
        onupdate=datetime.utcnow,
        nullable=False
    )