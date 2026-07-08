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


class DataPipelineStep(Base):

    __tablename__ = "data_pipeline_steps"

    __table_args__ = (

        UniqueConstraint(

            "pipeline_id",

            "step_order",

            name="uq_pipeline_step_order"
        ),

        UniqueConstraint(

            "pipeline_id",

            "step_code",

            name="uq_pipeline_step_code"
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

    output_storage_instance_id = Column(
        Integer,
        ForeignKey(
            "storage_instances.id",
            name=(
                "fk_data_pipeline_step_"
                "output_storage_instance_id"
            ),
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    configuration_json = Column(
        JSONB,
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