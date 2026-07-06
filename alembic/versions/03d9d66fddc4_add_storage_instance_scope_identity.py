"""add storage instance scope identity

Revision ID: 03d9d66fddc4
Revises: 70795fa72bd1
Create Date: 2026-07-04 10:45:34.109446
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "03d9d66fddc4"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "70795fa72bd1"

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
        "storage_instances",
        sa.Column(
            "scope_type",
            sa.String(length=50),
            server_default="PLATFORM",
            nullable=False,
        ),
    )

    op.drop_constraint(
        "uq_storage_instance_org_code",
        "storage_instances",
        type_="unique",
    )

    op.create_check_constraint(
        "ck_storage_instance_scope_identity",
        "storage_instances",
        """
        (
            scope_type = 'PLATFORM'
            AND organization_id IS NULL
            AND workspace_id IS NULL
        )
        OR
        (
            scope_type = 'ORGANIZATION'
            AND organization_id IS NOT NULL
            AND workspace_id IS NULL
        )
        OR
        (
            scope_type = 'WORKSPACE'
            AND organization_id IS NOT NULL
            AND workspace_id IS NOT NULL
        )
        """,
    )

    op.create_index(
        "ix_storage_instances_scope_type",
        "storage_instances",
        ["scope_type"],
        unique=False,
    )

    op.create_index(
        "uq_storage_instance_platform_code",
        "storage_instances",
        ["instance_code"],
        unique=True,
        postgresql_where=sa.text(
            "scope_type = 'PLATFORM'"
        ),
    )

    op.create_index(
        "uq_storage_instance_organization_code",
        "storage_instances",
        [
            "organization_id",
            "instance_code",
        ],
        unique=True,
        postgresql_where=sa.text(
            "scope_type = 'ORGANIZATION'"
        ),
    )

    op.create_index(
        "uq_storage_instance_workspace_code",
        "storage_instances",
        [
            "workspace_id",
            "instance_code",
        ],
        unique=True,
        postgresql_where=sa.text(
            "scope_type = 'WORKSPACE'"
        ),
    )


def downgrade() -> None:

    op.drop_index(
        "uq_storage_instance_workspace_code",
        table_name="storage_instances",
    )

    op.drop_index(
        "uq_storage_instance_organization_code",
        table_name="storage_instances",
    )

    op.drop_index(
        "uq_storage_instance_platform_code",
        table_name="storage_instances",
    )

    op.drop_index(
        "ix_storage_instances_scope_type",
        table_name="storage_instances",
    )

    op.drop_constraint(
        "ck_storage_instance_scope_identity",
        "storage_instances",
        type_="check",
    )

    op.create_unique_constraint(
        "uq_storage_instance_org_code",
        "storage_instances",
        [
            "organization_id",
            "instance_code",
        ],
    )

    op.drop_column(
        "storage_instances",
        "scope_type",
    )