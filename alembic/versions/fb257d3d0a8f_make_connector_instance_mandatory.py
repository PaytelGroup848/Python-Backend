"""make connector instance mandatory

Revision ID: fb257d3d0a8f
Revises: c20e82109506
Create Date: 2026-06-24 09:25:10.311891

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fb257d3d0a8f'
down_revision: Union[str, Sequence[str], None] = 'c20e82109506'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.alter_column(
        "corpus_sources",
        "connector_instance_id",
        existing_type=sa.Integer(),
        nullable=False
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column(
        "corpus_sources",
        "connector_instance_id",
        existing_type=sa.Integer(),
        nullable=True
    )
