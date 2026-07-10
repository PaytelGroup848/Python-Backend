"""align model artifacts with storage runtime

Revision ID: 31c9ec050170
Revises: 9f7d839cf6cd
Create Date: 2026-07-10 07:43:26.675042

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '31c9ec050170'
down_revision: Union[str, Sequence[str], None] = '9f7d839cf6cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "model_artifacts",
        sa.Column(
            "storage_instance_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "model_artifacts",
        sa.Column(
            "storage_reference",
            sa.String(length=2000),
            nullable=True,
        ),
    )

    op.add_column(
        "model_artifacts",
        sa.Column(
            "metadata_json",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
    )

    op.create_index(
        "ix_model_artifacts_storage_instance_id",
        "model_artifacts",
        ["storage_instance_id"],
        unique=False,
    )

    op.create_index(
        "ix_model_artifacts_storage_reference",
        "model_artifacts",
        ["storage_reference"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_model_artifacts_storage_instance_id",
        "model_artifacts",
        "storage_instances",
        ["storage_instance_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    op.create_check_constraint(
        "ck_model_artifacts_storage_lineage",
        "model_artifacts",
        """
        (
            storage_instance_id IS NOT NULL
            AND storage_reference IS NOT NULL
            AND btrim(storage_reference) <> ''
        )
        OR
        (
            artifact_path IS NOT NULL
            AND btrim(artifact_path) <> ''
        )
        """,
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_model_artifacts_storage_lineage",
        "model_artifacts",
        type_="check",
    )

    op.drop_constraint(
        "fk_model_artifacts_storage_instance_id",
        "model_artifacts",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_model_artifacts_storage_reference",
        table_name="model_artifacts",
    )

    op.drop_index(
        "ix_model_artifacts_storage_instance_id",
        table_name="model_artifacts",
    )

    op.drop_column(
        "model_artifacts",
        "metadata_json",
    )

    op.drop_column(
        "model_artifacts",
        "storage_reference",
    )

    op.drop_column(
        "model_artifacts",
        "storage_instance_id",
    )
    