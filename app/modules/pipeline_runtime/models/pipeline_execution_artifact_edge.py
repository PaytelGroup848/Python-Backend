from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)

from app.db.database import Base


class PipelineExecutionArtifactEdge(Base):

    __tablename__ = (
        "pipeline_execution_artifact_edges"
    )

    __table_args__ = (

        UniqueConstraint(
            "parent_artifact_id",
            "child_artifact_id",
            "relation_type",
            name=(
                "uq_pipeline_execution_"
                "artifact_edge"
            ),
        ),

    )

    id = Column(
        BigInteger,
        primary_key=True,
    )

    parent_artifact_id = Column(
        BigInteger,
        ForeignKey(
            "pipeline_execution_artifacts.id",
            name=(
                "fk_pipeline_artifact_"
                "edge_parent_id"
            ),
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    child_artifact_id = Column(
        BigInteger,
        ForeignKey(
            "pipeline_execution_artifacts.id",
            name=(
                "fk_pipeline_artifact_"
                "edge_child_id"
            ),
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    relation_type = Column(
        String(100),
        nullable=False,
        index=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
    )