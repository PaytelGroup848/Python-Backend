"""remove user plan and token limit

Revision ID: 86e350de9a4a
Revises: ea1143c72e65
Create Date: 2026-06-12 14:50:39.407589

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '86e350de9a4a'
down_revision: Union[str, Sequence[str], None] = 'ea1143c72e65'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    op.drop_column(
        "users",
        "plan_name"
    )

    op.drop_column(
        "users",
        "token_limit"
    )


def downgrade():

    op.add_column(
        "users",
        sa.Column(
            "plan_name",
            sa.String(),
            nullable=False,
            server_default="free"
        )
    )

    op.add_column(
        "users",
        sa.Column(
            "token_limit",
            sa.BigInteger(),
            nullable=False,
            server_default="1000000"
        )
    )
