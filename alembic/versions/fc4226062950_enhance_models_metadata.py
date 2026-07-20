"""enhance models metadata

Revision ID: fc4226062950
Revises: bd8184ed0ba4
Create Date: 2026-06-27 10:25:36.817479

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'fc4226062950'
down_revision: Union[str, Sequence[str], None] = 'bd8184ed0ba4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "models",
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default="DRAFT"
        )
    )

    op.add_column(
        "models",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now()
        )
    )

    op.create_index(
        "ix_models_status",
        "models",
        ["status"],
        unique=False
    )

    op.create_index(
        "ix_models_provider_id",
        "models",
        ["provider_id"],
        unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        "ix_models_provider_id",
        table_name="models"
    )

    op.drop_index(
        "ix_models_status",
        table_name="models"
    )

    op.drop_column(
        "models",
        "updated_at"
    )

    op.drop_column(
        "models",
        "status"
    )
