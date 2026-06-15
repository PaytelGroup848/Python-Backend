"""enhance invoices table

Revision ID: 6ce700d426f1
Revises: 25e963c28332
Create Date: 2026-06-12 11:27:23.199059

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ce700d426f1'
down_revision: Union[str, Sequence[str], None] = '25e963c28332'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.add_column(
        'invoices',
        sa.Column(
            'currency_symbol',
            sa.String(length=10),
            nullable=True
        )
    )

    op.add_column(
        'invoices',
        sa.Column(
            'period_start',
            sa.DateTime(),
            nullable=True
        )
    )

    op.add_column(
        'invoices',
        sa.Column(
            'period_end',
            sa.DateTime(),
            nullable=True
        )
    )

    op.add_column(
        'invoices',
        sa.Column(
            'external_reference',
            sa.String(length=255),
            nullable=True
        )
    )


def downgrade() -> None:

    op.drop_column(
        'invoices',
        'external_reference'
    )

    op.drop_column(
        'invoices',
        'period_end'
    )

    op.drop_column(
        'invoices',
        'period_start'
    )

    op.drop_column(
        'invoices',
        'currency_symbol'
    )
