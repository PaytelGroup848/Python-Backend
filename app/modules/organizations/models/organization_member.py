from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func
)

from app.db.database import Base


class OrganizationMember(Base):

    __tablename__ = "organization_members"

    __table_args__ = (

        UniqueConstraint(

            "organization_id",

            "user_id",

            name="uq_organization_member"

        ),

    )

    id = Column(

        Integer,

        primary_key=True,

        index=True

    )

    organization_id = Column(

        Integer,

        ForeignKey(

            "organizations.id",

            name="fk_org_member_organization_id"

        ),

        nullable=False,

        index=True

    )

    user_id = Column(

        Integer,

        ForeignKey(

            "users.id",

            name="fk_org_member_user_id"

        ),

        nullable=False,

        index=True

    )

    role = Column(

        String(50),

        nullable=False,

        index=True

    )

    is_owner = Column(

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

    joined_at = Column(

        DateTime,

        nullable=False,

        default=datetime.utcnow,

        server_default=func.now()

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