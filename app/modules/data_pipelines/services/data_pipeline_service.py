from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
)

from app.db.database import Base


class DataPipeline(Base):

    __tablename__ = "data_pipelines"

    id = Column(
        Integer,
        primary_key=True
    )

    corpus_id = Column(
        Integer,
        ForeignKey(
            "corpora.id",
            name="fk_pipeline_corpus_id"
        ),
        nullable=False,
        index=True
    )

    name = Column(
        String(255),
        nullable=False
    )

    version = Column(
        String(100),
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False,
        index=True
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