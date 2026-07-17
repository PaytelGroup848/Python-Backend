from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)

from sqlalchemy.orm import (
    relationship,
)

from app.db.database import Base

class Dataset(Base):

    __tablename__ = "datasets"

    __table_args__ = (

        UniqueConstraint(

            "corpus_id",

            "version",

            name="uq_dataset_corpus_version"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    corpus_id = Column(
        Integer,
        ForeignKey(
            "corpora.id",
            name="fk_dataset_corpus_id"
        ),
        nullable=False,
        index=True
    )

    name = Column(
        String(255),
        nullable=False
    )

    domain = Column(
        String(100),
        nullable=False,
        index=True
    )

    version = Column(
        String(50),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    source = Column(
        String(255),
        nullable=True
    )

    record_count = Column(
        Integer,
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    uploads = relationship(
        "DatasetUpload",
        back_populates="dataset",
        cascade="all, delete-orphan",
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )