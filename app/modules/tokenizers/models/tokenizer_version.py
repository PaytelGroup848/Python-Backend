from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)

from sqlalchemy.dialects.postgresql import (
    JSONB,
)

from app.db.database import (
    Base,
)


class TokenizerVersion(
    Base
):

    __tablename__ = (
        "tokenizer_versions"
    )

    __table_args__ = (

        UniqueConstraint(
            "tokenizer_id",
            "version",
            name=(
                "uq_tokenizer_versions_"
                "tokenizer_version"
            ),
        ),

        UniqueConstraint(
            "tokenizer_training_job_id",
            name=(
                "uq_tokenizer_versions_"
                "training_job_id"
            ),
        ),

    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    tokenizer_id = Column(
        Integer,
        ForeignKey(
            "tokenizers.id",
            name=(
                "fk_tokenizer_versions_"
                "tokenizer_id"
            ),
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    tokenizer_training_job_id = Column(
        Integer,
        ForeignKey(
            "tokenizer_training_jobs.id",
            name=(
                "fk_tokenizer_versions_"
                "training_job_id"
            ),
            ondelete="RESTRICT",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    version = Column(
        String(100),
        nullable=False,
    )

    display_name = Column(
        String(255),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    status = Column(
        String(50),
        nullable=False,
        index=True,
    )

    vocabulary_size = Column(
        Integer,
        nullable=False,
    )

    content_hash = Column(
        String(255),
        nullable=False,
        index=True,
    )

    version_metadata_json = Column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    is_immutable = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
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