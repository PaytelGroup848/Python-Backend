"""add model version lifecycle columns

Revision ID: a0f16de552a5
Revises: e0140ed569d5
Create Date: 2026-07-13 05:03:03.657466

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a0f16de552a5'
down_revision: Union[str, Sequence[str], None] = 'e0140ed569d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "model_versions",
        sa.Column(
            "training_job_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "model_versions",
        sa.Column(
            "artifact_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "model_versions",
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default="CREATED",
        ),
    )

    op.add_column(
        "model_versions",
        sa.Column(
            "is_release_ready",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )

    op.add_column(
        "model_versions",
        sa.Column(
            "is_deployment_ready",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )

    op.add_column(
        "model_versions",
        sa.Column(
            "parent_model_version_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_index(
        op.f("ix_model_versions_training_job_id"),
        "model_versions",
        ["training_job_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_model_versions_artifact_id"),
        "model_versions",
        ["artifact_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_model_versions_status"),
        "model_versions",
        ["status"],
        unique=False,
    )

    op.create_index(
        op.f("ix_model_versions_parent_model_version_id"),
        "model_versions",
        ["parent_model_version_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_model_version_training_job_id",
        "model_versions",
        "training_jobs",
        ["training_job_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_foreign_key(
        "fk_model_version_artifact_id",
        "model_versions",
        "model_artifacts",
        ["artifact_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_foreign_key(
        "fk_model_version_parent_model_version_id",
        "model_versions",
        "model_versions",
        ["parent_model_version_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_model_version_parent_model_version_id",
        "model_versions",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_model_version_artifact_id",
        "model_versions",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_model_version_training_job_id",
        "model_versions",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_model_versions_parent_model_version_id"),
        table_name="model_versions",
    )

    op.drop_index(
        op.f("ix_model_versions_status"),
        table_name="model_versions",
    )

    op.drop_index(
        op.f("ix_model_versions_artifact_id"),
        table_name="model_versions",
    )

    op.drop_index(
        op.f("ix_model_versions_training_job_id"),
        table_name="model_versions",
    )

    op.drop_column(
        "model_versions",
        "parent_model_version_id",
    )

    op.drop_column(
        "model_versions",
        "is_deployment_ready",
    )

    op.drop_column(
        "model_versions",
        "is_release_ready",
    )

    op.drop_column(
        "model_versions",
        "status",
    )

    op.drop_column(
        "model_versions",
        "artifact_id",
    )

    op.drop_column(
        "model_versions",
        "training_job_id",
    )
