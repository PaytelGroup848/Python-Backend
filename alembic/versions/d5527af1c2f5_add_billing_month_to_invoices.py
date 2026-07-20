"""add billing_month to invoices

Revision ID: d5527af1c2f5
Revises: 6ce700d426f1
Create Date: 2026-06-16 11:14:54.442277

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'd5527af1c2f5'
down_revision: Union[str, Sequence[str], None] = '6ce700d426f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_index(
        op.f("ix_invoices_billing_month"),
        "invoices",
        ["billing_month"],
        unique=False
    )


def downgrade() -> None:

    op.drop_index(
        op.f("ix_invoices_billing_month"),
        table_name="invoices"
    )