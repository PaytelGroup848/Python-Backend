"""bind pipeline artifacts to storage instances

Revision ID: 1ebc2455f7ce
Revises: 03d9d66fddc4
Create Date: 2026-07-04 12:33:15.925243

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "1ebc2455f7ce"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "03d9d66fddc4"

branch_labels: Union[
    str,
    Sequence[str],
    None,
] = None

depends_on: Union[
    str,
    Sequence[str],
    None,
] = None


def upgrade() -> None:

    op.add_column(
        "pipeline_execution_artifacts",
        sa.Column(
            "storage_instance_id",
            sa.Integer(),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_pipeline_execution_artifacts_storage_instance_id",
        "pipeline_execution_artifacts",
        [
            "storage_instance_id",
        ],
        unique=False,
    )

    op.create_foreign_key(
        "fk_pipeline_execution_artifact_storage_instance_id",
        "pipeline_execution_artifacts",
        "storage_instances",
        [
            "storage_instance_id",
        ],
        [
            "id",
        ],
        ondelete="RESTRICT",
    )


def downgrade() -> None:

    op.drop_constraint(
        "fk_pipeline_execution_artifact_storage_instance_id",
        "pipeline_execution_artifacts",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_pipeline_execution_artifacts_storage_instance_id",
        table_name="pipeline_execution_artifacts",
    )

    op.drop_column(
        "pipeline_execution_artifacts",
        "storage_instance_id",
    )