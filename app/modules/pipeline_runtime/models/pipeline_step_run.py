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
from sqlalchemy.dialects.postgresql import JSONB

class PipelineStepRun(Base):

    __tablename__ = "pipeline_step_runs"

    __table_args__ = (

        UniqueConstraint(

            "pipeline_run_id",

            "pipeline_step_id",

            name="uq_pipeline_step_run"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    pipeline_run_id = Column(
        Integer,
        ForeignKey(
            "pipeline_runs.id",
            name="fk_pipeline_step_run_pipeline_run_id"
        ),
        nullable=False,
        index=True
    )

    pipeline_step_id = Column(
        Integer,
        ForeignKey(
            "data_pipeline_steps.id",
            name="fk_pipeline_step_run_step_id"
        ),
        nullable=False,
        index=True
    )

    step_run_code = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True
    )

    execution_order = Column(
        Integer,
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False,
        index=True
    )

    metrics_json = Column(
        JSONB,
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

    error_message = Column(
        String,
        nullable=True
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