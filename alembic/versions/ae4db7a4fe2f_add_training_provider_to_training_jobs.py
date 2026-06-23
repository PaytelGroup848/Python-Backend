"""add training provider to training jobs

Revision ID: ae4db7a4fe2f
Revises: 52c7d85947de
Create Date: 2026-06-22 08:34:15.431037

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ae4db7a4fe2f'
down_revision: Union[str, Sequence[str], None] = '52c7d85947de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    op.add_column(
        'training_jobs',
        sa.Column(
            'training_provider_id',
            sa.Integer(),
            nullable=True
        )
    )

    op.create_index(
        op.f(
            'ix_training_jobs_training_provider_id'
        ),
        'training_jobs',
        ['training_provider_id'],
        unique=False
    )

    op.create_foreign_key(
        'fk_training_job_provider_id',
        'training_jobs',
        'training_providers',
        ['training_provider_id'],
        ['id']
    )
    # ### end Alembic commands ###


def downgrade():

    op.drop_constraint(
        'fk_training_job_provider_id',
        'training_jobs',
        type_='foreignkey'
    )

    op.drop_index(
        op.f(
            'ix_training_jobs_training_provider_id'
        ),
        table_name='training_jobs'
    )

    op.drop_column(
        'training_jobs',
        'training_provider_id'
    )
   
    # ### end Alembic commands ###
