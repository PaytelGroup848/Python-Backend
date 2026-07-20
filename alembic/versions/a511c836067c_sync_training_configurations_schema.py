"""sync training_configurations schema

Revision ID: a511c836067c
Revises: 624e043db673
Create Date: 2026-07-18 06:16:11.026615

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a511c836067c'
down_revision: Union[str, Sequence[str], None] = '624e043db673'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "training_configurations",
        sa.Column("description", sa.String(length=500), nullable=True),
    )

    op.add_column(
        "training_configurations",
        sa.Column("display_name", sa.String(length=200), nullable=True),
    )

    op.add_column(
        "training_configurations",
        sa.Column("created_by", sa.String(length=150), nullable=True),
    )

    op.add_column(
        "training_configurations",
        sa.Column("updated_by", sa.String(length=150), nullable=True),
    )

    op.add_column(
        "training_configurations",
        sa.Column("published_at", sa.DateTime(), nullable=True),
    )

    op.add_column(
        "training_configurations",
        sa.Column("published_by", sa.String(length=150), nullable=True),
    )

    op.add_column(
        "training_configurations",
        sa.Column(
            "is_system",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    # Populate existing rows
    op.execute("""
        UPDATE training_configurations
        SET
            display_name = configuration_code,
            created_by = 'system'
        WHERE display_name IS NULL
           OR created_by IS NULL;
    """)

    # Enforce NOT NULL after backfill
    op.alter_column(
        "training_configurations",
        "display_name",
        nullable=False,
    )

    op.alter_column(
        "training_configurations",
        "created_by",
        nullable=False,
    )


def downgrade():
    op.drop_column("training_configurations", "is_system")
    op.drop_column("training_configurations", "published_by")
    op.drop_column("training_configurations", "published_at")
    op.drop_column("training_configurations", "updated_by")
    op.drop_column("training_configurations", "created_by")
    op.drop_column("training_configurations", "display_name")
    op.drop_column("training_configurations", "description")
