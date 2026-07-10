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


class TokenizerTrainingConfiguration(
    Base
):

    __tablename__ = (
        "tokenizer_training_configurations"
    )

    __table_args__ = (

        UniqueConstraint(
            "configuration_code",
            "version",
            name=(
                "uq_tokenizer_training_"
                "configuration_code_version"
            ),
        ),

    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    tokenizer_implementation_id = Column(
        Integer,
        ForeignKey(
            "tokenizer_implementations.id",
            name=(
                "fk_tokenizer_training_configuration_"
                "implementation_id"
            ),
            ondelete="RESTRICT",
        ),
        nullable=False,
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