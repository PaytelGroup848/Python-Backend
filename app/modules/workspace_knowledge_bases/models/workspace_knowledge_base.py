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


class WorkspaceKnowledgeBase(Base):

    __tablename__ = "workspace_knowledge_bases"

    __table_args__ = (

        UniqueConstraint(

            "workspace_id",

            "knowledge_base_id",

            name="uq_workspace_knowledge_base"

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

            name="fk_workspace_kb_workspace_id"

        ),

        nullable=False,

        index=True

    )

    knowledge_base_id = Column(

        Integer,

        ForeignKey(

            "knowledge_bases.id",

            name="fk_workspace_kb_knowledge_base_id"

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