from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)

from sqlalchemy.dialects.postgresql import (
    JSONB,
)

from app.db.database import (
    Base,
)


class TrainingConfiguration(
    Base
):

    __tablename__ = (
        "training_configurations"
    )

    __table_args__ = (

        UniqueConstraint(
            "configuration_code",
            "version",
            name=(
                "uq_training_configuration_"
                "code_version"
            ),
        ),

    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    configuration_code = Column(
        String(150),
        nullable=False,
        index=True,
    )

    version = Column(
        Integer,
        nullable=False,
    )

    training_type = Column(
        String(100),
        nullable=False,
        index=True,
    )

    runtime_code = Column(
        String(100),
        nullable=False,
        index=True,
    )

    configuration_json = Column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        index=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
        onupdate=datetime.utcnow,
    )