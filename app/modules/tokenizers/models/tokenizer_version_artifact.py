from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)

from sqlalchemy.dialects.postgresql import (
    JSONB,
)

from app.db.database import (
    Base,
)


class TokenizerVersionArtifact(
    Base
):

    __tablename__ = (
        "tokenizer_version_artifacts"
    )

    __table_args__ = (

        UniqueConstraint(
            "tokenizer_version_id",
            "artifact_code",
            name=(
                "uq_tokenizer_version_artifacts_"
                "version_code"
            ),
        ),

    )

    id = Column(
        BigInteger,
        primary_key=True,
    )

    tokenizer_version_id = Column(
        Integer,
        ForeignKey(
            "tokenizer_versions.id",
            name=(
                "fk_tokenizer_version_artifacts_"
                "tokenizer_version_id"
            ),
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    storage_instance_id = Column(
        Integer,
        ForeignKey(
            "storage_instances.id",
            name=(
                "fk_tokenizer_version_artifacts_"
                "storage_instance_id"
            ),
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    artifact_code = Column(
        String(255),
        nullable=False,
        index=True,
    )

    artifact_type = Column(
        String(100),
        nullable=False,
        index=True,
    )

    storage_reference = Column(
        String(2000),
        nullable=False,
    )

    mime_type = Column(
        String(255),
        nullable=True,
    )

    size_bytes = Column(
        BigInteger,
        nullable=True,
    )

    checksum = Column(
        String(255),
        nullable=False,
        index=True,
    )

    metadata_json = Column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
    )