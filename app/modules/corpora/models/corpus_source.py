from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint
)

from app.db.database import Base


class CorpusSource(Base):

    __tablename__ = "corpus_sources"

    __table_args__ = (

        UniqueConstraint(

            "corpus_id",

            "source_reference",

            name="uq_corpus_source_reference"
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
            name="fk_corpus_source_corpus_id"
        ),
        nullable=False,
        index=True
    )

    source_type = Column(
        String(100),
        nullable=False,
        index=True
    )

    source_reference = Column(
        String(1000),
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

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )