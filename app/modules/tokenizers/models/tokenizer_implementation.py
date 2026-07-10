from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)

from sqlalchemy.dialects.postgresql import (
    JSONB,
)

from app.db.database import (
    Base,
)


class TokenizerImplementation(
    Base
):

    __tablename__ = (
        "tokenizer_implementations"
    )

    __table_args__ = (

        UniqueConstraint(
            "implementation_code",
            "implementation_version",
            name=(
                "uq_tokenizer_implementation_"
                "code_version"
            ),
        ),

    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    implementation_code = Column(
        String(150),
        nullable=False,
        index=True,
    )

    implementation_version = Column(
        String(100),
        nullable=False,
    )

    display_name = Column(
        String(255),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    algorithm_type = Column(
        String(100),
        nullable=False,
        index=True,
    )

    trainer_class = Column(
        String(500),
        nullable=False,
    )

    tokenizer_class = Column(
        String(500),
        nullable=False,
    )

    training_configuration_schema_json = Column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    runtime_configuration_schema_json = Column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    capabilities_json = Column(
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