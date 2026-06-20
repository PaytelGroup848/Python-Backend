"""create assistants table

Revision ID: ad2683a19e0d
Revises: 1c1436417a3b
Create Date: 2026-06-18 06:25:55.543801

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ad2683a19e0d'
down_revision: Union[str, Sequence[str], None] = '1c1436417a3b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        'assistants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('system_prompt', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        op.f('ix_assistants_code'),
        'assistants',
        ['code'],
        unique=True
    )

    op.create_index(
        op.f('ix_assistants_id'),
        'assistants',
        ['id'],
        unique=False
    )

def downgrade() -> None:

    op.drop_index(
        op.f('ix_assistants_id'),
        table_name='assistants'
    )

    op.drop_index(
        op.f('ix_assistants_code'),
        table_name='assistants'
    )

    op.drop_table(
        'assistants'
    )
