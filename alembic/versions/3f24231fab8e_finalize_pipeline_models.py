"""finalize pipeline models

Revision ID: 3f24231fab8e
Revises: f5af4b9f71b6
Create Date: 2026-06-24 11:14:01.062892

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3f24231fab8e'
down_revision: Union[str, Sequence[str], None] = 'f5af4b9f71b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.alter_column(
        'data_pipeline_steps',
        'configuration_json',
        existing_type=sa.VARCHAR(),
        type_=postgresql.JSONB(
            astext_type=sa.Text()
        ),
        existing_nullable=True,
        postgresql_using='configuration_json::jsonb'
    )

    op.create_unique_constraint(
        'uq_pipeline_step_code',
        'data_pipeline_steps',
        ['pipeline_id', 'step_code']
    )
    # ### end Alembic commands ###


def downgrade() -> None:

    op.drop_constraint(
        'uq_pipeline_step_code',
        'data_pipeline_steps',
        type_='unique'
    )

    op.alter_column(
        'data_pipeline_steps',
        'configuration_json',
        existing_type=postgresql.JSONB(
            astext_type=sa.Text()
        ),
        type_=sa.VARCHAR(),
        existing_nullable=True
    )
    # ### end Alembic commands ###
