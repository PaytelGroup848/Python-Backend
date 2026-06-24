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


class DataPipelineStep(Base):

    __tablename__ = "data_pipeline_steps"

    __table_args__ = (

        UniqueConstraint(

            "pipeline_id",

            "step_order",

            name="uq_pipeline_step_order"
        ),
    )

    id = Column(
        Integer,
        primary_key=True
    )

    pipeline_id = Column(
        Integer,
        ForeignKey(
            "data_pipelines.id",
            name="fk_pipeline_step_pipeline_id"
        ),
        nullable=False,
        index=True
    )

    step_order = Column(
        Integer,
        nullable=False
    )

    step_code = Column(
        String(100),
        nullable=False,
        index=True
    )

    step_type = Column(
        String(100),
        nullable=False,
        index=True
    )

    runtime_code = Column(
        String(100),
        nullable=False,
        index=True
    )

    configuration_json = Column(
        String,
        nullable=True
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