"""drop usage limits table

Revision ID: ea1143c72e65
Revises: a2452f670199
Create Date: 2026-06-12 12:10:10.143039

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ea1143c72e65'
down_revision: Union[str, Sequence[str], None] = 'a2452f670199'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.drop_table(
        "usage_limits"
    )


def downgrade() -> None:
    """Downgrade schema."""

    pass
