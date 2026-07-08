from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
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


class DatasetSnapshot(
    Base
):

    __tablename__ = "dataset_snapshots"

    __table_args__ = (

        UniqueConstraint(
            "dataset_id",
            "snapshot_code",
            name=(
                "uq_dataset_snapshot_"
                "dataset_code"
            ),
        ),

    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    dataset_id = Column(
        Integer,
        ForeignKey(
            "datasets.id",
            name=(
                "fk_dataset_snapshot_"
                "dataset_id"
            ),
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    snapshot_code = Column(
        String(150),
        nullable=False,
        index=True,
    )

    status = Column(
        String(50),
        nullable=False,
        index=True,
    )

    record_count = Column(
        BigInteger,
        nullable=False,
    )

    max_record_id = Column(
        BigInteger,
        nullable=True,
    )

    content_hash = Column(
        String(255),
        nullable=False,
        index=True,
    )

    snapshot_metadata_json = Column(
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

    frozen_at = Column(
        DateTime,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
    )