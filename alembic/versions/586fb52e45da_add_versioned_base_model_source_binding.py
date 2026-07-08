"""add versioned base model source binding

Revision ID: 586fb52e45da
Revises: 4270a9462397
Create Date: 2026-07-07 05:18:18.730504
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "586fb52e45da"
down_revision: Union[str, Sequence[str], None] = "4270a9462397"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "model_versions",
        sa.Column(
            "source_type",
            sa.String(length=50),
            nullable=True,
        ),
    )

    op.add_column(
        "model_versions",
        sa.Column(
            "source_uri",
            sa.String(length=1000),
            nullable=True,
        ),
    )

    op.add_column(
        "model_versions",
        sa.Column(
            "source_revision",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.create_index(
        op.f("ix_model_versions_source_type"),
        "model_versions",
        ["source_type"],
        unique=False,
    )

    op.add_column(
        "training_jobs",
        sa.Column(
            "base_model_version_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_index(
        op.f("ix_training_jobs_base_model_version_id"),
        "training_jobs",
        ["base_model_version_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_training_job_base_model_version_id",
        "training_jobs",
        "model_versions",
        ["base_model_version_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_training_job_base_model_version_id",
        "training_jobs",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_training_jobs_base_model_version_id"),
        table_name="training_jobs",
    )

    op.drop_column(
        "training_jobs",
        "base_model_version_id",
    )

    op.drop_index(
        op.f("ix_model_versions_source_type"),
        table_name="model_versions",
    )

    op.drop_column(
        "model_versions",
        "source_revision",
    )

    op.drop_column(
        "model_versions",
        "source_uri",
    )

    op.drop_column(
        "model_versions",
        "source_type",
    )