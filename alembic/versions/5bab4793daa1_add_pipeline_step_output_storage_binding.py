"""add pipeline step output storage binding

Revision ID: 5bab4793daa1
Revises: 1ebc2455f7ce
Create Date: 2026-07-06 07:18:01.887764

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5bab4793daa1'
down_revision: Union[str, Sequence[str], None] = '1ebc2455f7ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "data_pipeline_steps",
        sa.Column(
            "output_storage_instance_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_data_pipeline_steps_output_storage_instance_id",
        "data_pipeline_steps",
        ["output_storage_instance_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_data_pipeline_step_output_storage_instance_id",
        "data_pipeline_steps",
        "storage_instances",
        ["output_storage_instance_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_data_pipeline_step_output_storage_instance_id",
        "data_pipeline_steps",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_data_pipeline_steps_output_storage_instance_id",
        table_name="data_pipeline_steps",
    )

    op.drop_column(
        "data_pipeline_steps",
        "output_storage_instance_id",
    )
