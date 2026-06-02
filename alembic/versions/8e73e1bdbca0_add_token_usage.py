"""add_token_usage

Revision ID: 8e73e1bdbca0
Revises: 3246eef94f4a
Create Date: 2026-06-02 09:48:30.639186

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8e73e1bdbca0'
down_revision: Union[str, Sequence[str], None] = '3246eef94f4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        'token_usage',

        sa.Column(
            'id',
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            'user_id',
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            'provider',
            sa.String(),
            nullable=False
        ),

        sa.Column(
            'model',
            sa.String(),
            nullable=False
        ),

        sa.Column(
            'prompt_tokens',
            sa.Integer(),
            nullable=True
        ),

        sa.Column(
            'completion_tokens',
            sa.Integer(),
            nullable=True
        ),

        sa.Column(
            'total_tokens',
            sa.Integer(),
            nullable=True
        ),

        sa.Column(
            'created_at',
            sa.DateTime(),
            nullable=True
        ),

        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id']
        ),

        sa.PrimaryKeyConstraint(
            'id'
        )
    )

    op.create_index(
        op.f('ix_token_usage_id'),
        'token_usage',
        ['id'],
        unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:

    op.drop_index(
        op.f('ix_token_usage_id'),
        table_name='token_usage'
    )

    op.drop_table(
        'token_usage'
    )
    # ### end Alembic commands ###
