from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    UniqueConstraint,
    func
)

from app.db.database import Base


class WorkspaceModel(Base):

    __tablename__ = "workspace_models"

    __table_args__ = (

        UniqueConstraint(

            "workspace_id",

            "model_release_id",

            name="uq_workspace_model"

        ),

    )

    id = Column(

        Integer,

        primary_key=True,

        index=True

    )

    workspace_id = Column(

        Integer,

        ForeignKey(

            "workspaces.id",

            name="fk_workspace_model_workspace_id"

        ),

        nullable=False,

        index=True

    )

    model_release_id = Column(

        Integer,

        ForeignKey(

            "model_releases.id",

            name="fk_workspace_model_release_id"

        ),

        nullable=False,

        index=True

    )

    priority = Column(
        Integer,
        nullable=False,
        default=100,
        server_default="100"
    )

    is_default = Column(

        Boolean,

        nullable=False,

        default=False,

        server_default="false"

    )

    is_active = Column(

        Boolean,

        nullable=False,

        default=True,

        server_default="true"

    )

    created_at = Column(

        DateTime,

        nullable=False,

        default=datetime.utcnow,

        server_default=func.now()

    )

    updated_at = Column(

        DateTime,

        nullable=False,

        default=datetime.utcnow,

        server_default=func.now(),

        onupdate=datetime.utcnow

    )