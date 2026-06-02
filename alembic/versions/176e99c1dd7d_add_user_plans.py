"""add_user_plans

Revision ID: 176e99c1dd7d
Revises: 8e73e1bdbca0
Create Date: 2026-06-02 11:05:31.711664

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '176e99c1dd7d'
down_revision: Union[str, Sequence[str], None] = '8e73e1bdbca0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        'users',
        sa.Column(
            'plan_name',
            sa.String(),
            nullable=False,
            server_default='free'
        )
    )

    op.add_column(
        'users',
        sa.Column(
            'token_limit',
            sa.BigInteger(),
            nullable=False,
            server_default='1000000'
        )
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        'users',
        'token_limit'
    )

    op.drop_column(
        'users',
        'plan_name'
    )
    # ### end Alembic commands ###
