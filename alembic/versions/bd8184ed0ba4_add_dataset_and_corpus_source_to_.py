"""add_dataset_and_corpus_source_to_pipeline_run

Revision ID: bd8184ed0ba4
Revises: 3f24231fab8e
Create Date: 2026-06-26 06:27:03.987262

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'bd8184ed0ba4'
down_revision: Union[str, Sequence[str], None] = '3f24231fab8e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "pipeline_runs",
        sa.Column(
            "dataset_id",
            sa.Integer(),
            nullable=True
        )
    )

    op.add_column(
        "pipeline_runs",
        sa.Column(
            "corpus_source_id",
            sa.Integer(),
            nullable=True
        )
    )

    op.create_index(
        op.f("ix_pipeline_runs_dataset_id"),
        "pipeline_runs",
        ["dataset_id"],
        unique=False
    )

    op.create_index(
        op.f("ix_pipeline_runs_corpus_source_id"),
        "pipeline_runs",
        ["corpus_source_id"],
        unique=False
    )

    op.create_foreign_key(
        "fk_pipeline_run_dataset_id",
        "pipeline_runs",
        "datasets",
        ["dataset_id"],
        ["id"]
    )

    op.create_foreign_key(
        "fk_pipeline_run_corpus_source_id",
        "pipeline_runs",
        "corpus_sources",
        ["corpus_source_id"],
        ["id"]
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_pipeline_run_corpus_source_id",
        "pipeline_runs",
        type_="foreignkey"
    )

    op.drop_constraint(
        "fk_pipeline_run_dataset_id",
        "pipeline_runs",
        type_="foreignkey"
    )

    op.drop_index(
        op.f("ix_pipeline_runs_corpus_source_id"),
        table_name="pipeline_runs"
    )

    op.drop_index(
        op.f("ix_pipeline_runs_dataset_id"),
        table_name="pipeline_runs"
    )

    op.drop_column(
        "pipeline_runs",
        "corpus_source_id"
    )

    op.drop_column(
        "pipeline_runs",
        "dataset_id"
    )