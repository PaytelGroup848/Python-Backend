"""remove redundant primary key indexes

Revision ID: f5af4b9f71b6
Revises: fb257d3d0a8f
Create Date: 2026-06-24 09:47:07.025903

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'f5af4b9f71b6'
down_revision: Union[str, Sequence[str], None] = 'fb257d3d0a8f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.drop_index(
        "ix_corpus_sources_id",
        table_name="corpus_sources"
    )

    op.drop_index(
        "ix_pipeline_runs_id",
        table_name="pipeline_runs"
    )

    op.drop_index(
        "ix_pipeline_step_runs_id",
        table_name="pipeline_step_runs"
    )

def downgrade() -> None:

    op.create_index(
        "ix_corpus_sources_id",
        "corpus_sources",
        ["id"],
        unique=False
    )

    op.create_index(
        "ix_pipeline_runs_id",
        "pipeline_runs",
        ["id"],
        unique=False
    )

    op.create_index(
        "ix_pipeline_step_runs_id",
        "pipeline_step_runs",
        ["id"],
        unique=False
    )
