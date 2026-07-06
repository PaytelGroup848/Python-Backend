"""add storage registry

Revision ID: 70795fa72bd1
Revises: 32742a4fceb8
Create Date: 2026-07-04 09:57:54.199010

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "70795fa72bd1"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "32742a4fceb8"

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

    #
    # STORAGE IMPLEMENTATIONS
    #

    op.create_table(
        "storage_implementations",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "implementation_code",
            sa.String(length=150),
            nullable=False,
        ),

        sa.Column(
            "implementation_version",
            sa.String(length=100),
            nullable=False,
        ),

        sa.Column(
            "display_name",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "runtime_type",
            sa.String(length=100),
            nullable=False,
        ),

        sa.Column(
            "configuration_schema_json",
            postgresql.JSONB(
                astext_type=sa.Text()
            ),
            server_default=sa.text(
                "'{}'::jsonb"
            ),
            nullable=False,
        ),

        sa.Column(
            "capabilities_json",
            postgresql.JSONB(
                astext_type=sa.Text()
            ),
            server_default=sa.text(
                "'{}'::jsonb"
            ),
            nullable=False,
        ),

        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),

        sa.PrimaryKeyConstraint(
            "id"
        ),

        sa.UniqueConstraint(
            "implementation_code",
            "implementation_version",
            name=(
                "uq_storage_"
                "implementation_code_version"
            ),
        ),
    )

    op.create_index(
        op.f(
            "ix_storage_implementations_id"
        ),
        "storage_implementations",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_storage_implementations_implementation_code"
        ),
        "storage_implementations",
        ["implementation_code"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_storage_implementations_runtime_type"
        ),
        "storage_implementations",
        ["runtime_type"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_storage_implementations_is_active"
        ),
        "storage_implementations",
        ["is_active"],
        unique=False,
    )

    #
    # STORAGE INSTANCES
    #

    op.create_table(
        "storage_instances",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "storage_implementation_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "organization_id",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "workspace_id",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "instance_code",
            sa.String(length=150),
            nullable=False,
        ),

        sa.Column(
            "display_name",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "configuration_json",
            postgresql.JSONB(
                astext_type=sa.Text()
            ),
            server_default=sa.text(
                "'{}'::jsonb"
            ),
            nullable=False,
        ),

        sa.Column(
            "secret_reference",
            sa.String(length=1000),
            nullable=True,
        ),

        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ["storage_implementation_id"],
            ["storage_implementations.id"],
            name=(
                "fk_storage_instance_"
                "implementation_id"
            ),
        ),

        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=(
                "fk_storage_instance_"
                "organization_id"
            ),
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["workspace_id"],
            ["workspaces.id"],
            name=(
                "fk_storage_instance_"
                "workspace_id"
            ),
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint(
            "id"
        ),

        sa.UniqueConstraint(
            "organization_id",
            "instance_code",
            name=(
                "uq_storage_instance_org_code"
            ),
        ),
    )

    op.create_index(
        op.f(
            "ix_storage_instances_id"
        ),
        "storage_instances",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_storage_instances_storage_implementation_id"
        ),
        "storage_instances",
        ["storage_implementation_id"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_storage_instances_organization_id"
        ),
        "storage_instances",
        ["organization_id"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_storage_instances_workspace_id"
        ),
        "storage_instances",
        ["workspace_id"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_storage_instances_instance_code"
        ),
        "storage_instances",
        ["instance_code"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_storage_instances_is_active"
        ),
        "storage_instances",
        ["is_active"],
        unique=False,
    )


def downgrade() -> None:

    #
    # STORAGE INSTANCES
    #

    op.drop_index(
        op.f(
            "ix_storage_instances_is_active"
        ),
        table_name="storage_instances",
    )

    op.drop_index(
        op.f(
            "ix_storage_instances_instance_code"
        ),
        table_name="storage_instances",
    )

    op.drop_index(
        op.f(
            "ix_storage_instances_workspace_id"
        ),
        table_name="storage_instances",
    )

    op.drop_index(
        op.f(
            "ix_storage_instances_organization_id"
        ),
        table_name="storage_instances",
    )

    op.drop_index(
        op.f(
            "ix_storage_instances_storage_implementation_id"
        ),
        table_name="storage_instances",
    )

    op.drop_index(
        op.f(
            "ix_storage_instances_id"
        ),
        table_name="storage_instances",
    )

    op.drop_table(
        "storage_instances"
    )

    #
    # STORAGE IMPLEMENTATIONS
    #

    op.drop_index(
        op.f(
            "ix_storage_implementations_is_active"
        ),
        table_name="storage_implementations",
    )

    op.drop_index(
        op.f(
            "ix_storage_implementations_runtime_type"
        ),
        table_name="storage_implementations",
    )

    op.drop_index(
        op.f(
            "ix_storage_implementations_implementation_code"
        ),
        table_name="storage_implementations",
    )

    op.drop_index(
        op.f(
            "ix_storage_implementations_id"
        ),
        table_name="storage_implementations",
    )

    op.drop_table(
        "storage_implementations"
    )