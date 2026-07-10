from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)

from app.db.database import (
    Base,
)


class TokenizerTrainingJob(
    Base
):

    __tablename__ = (
        "tokenizer_training_jobs"
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    dataset_snapshot_id = Column(
        Integer,
        ForeignKey(
            "dataset_snapshots.id",
            name=(
                "fk_tokenizer_training_jobs_"
                "dataset_snapshot_id"
            ),
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    tokenizer_training_configuration_id = Column(
        Integer,
        ForeignKey(
            "tokenizer_training_configurations.id",
            name=(
                "fk_tokenizer_training_jobs_"
                "training_configuration_id"
            ),
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    status = Column(
        String(50),
        nullable=False,
        index=True,
    )

    priority = Column(
        Integer,
        nullable=False,
        default=100,
        server_default="100",
        index=True,
    )

    created_by = Column(
        String(255),
        nullable=True,
    )

    failure_message = Column(
        Text,
        nullable=True,
    )

    started_at = Column(
        DateTime,
        nullable=True,
    )

    completed_at = Column(
        DateTime,
        nullable=True,
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