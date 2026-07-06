"""add tenant foundation

Revision ID: 32742a4fceb8
Revises: 243a01813e73
Create Date: 2026-07-04 09:51:58.077107

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "32742a4fceb8"

down_revision: Union[
    str,
    Sequence[str],
    None
] = "243a01813e73"

branch_labels: Union[
    str,
    Sequence[str],
    None
] = None

depends_on: Union[
    str,
    Sequence[str],
    None
] = None


def upgrade() -> None:

    #
    # ORGANIZATIONS
    #

    op.create_table(
        "organizations",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "code",
            sa.String(length=100),
            nullable=False
        ),

        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False
        ),

        sa.Column(
            "slug",
            sa.String(length=255),
            nullable=False
        ),

        sa.Column(
            "description",
            sa.Text(),
            nullable=True
        ),

        sa.Column(
            "logo_url",
            sa.String(length=1000),
            nullable=True
        ),

        sa.Column(
            "website",
            sa.String(length=500),
            nullable=True
        ),

        sa.Column(
            "email",
            sa.String(length=255),
            nullable=True
        ),

        sa.Column(
            "phone",
            sa.String(length=50),
            nullable=True
        ),

        sa.Column(
            "country",
            sa.String(length=100),
            nullable=True
        ),

        sa.Column(
            "timezone",
            sa.String(length=100),
            nullable=True
        ),

        sa.Column(
            "organization_type",
            sa.String(length=50),
            server_default="PERSONAL",
            nullable=False
        ),

        sa.Column(
            "status",
            sa.String(length=50),
            server_default="ACTIVE",
            nullable=False
        ),

        sa.Column(
            "is_system",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False
        ),

        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False
        ),

        sa.Column(
            "created_by",
            sa.String(length=255),
            nullable=True
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False
        ),

        sa.PrimaryKeyConstraint(
            "id"
        ),

        sa.UniqueConstraint(
            "code",
            name="uq_organizations_code"
        ),

        sa.UniqueConstraint(
            "slug",
            name="uq_organizations_slug"
        ),
    )

    op.create_index(
        "ix_organizations_id",
        "organizations",
        ["id"],
        unique=False
    )

    op.create_index(
        "ix_organizations_code",
        "organizations",
        ["code"],
        unique=False
    )

    op.create_index(
        "ix_organizations_slug",
        "organizations",
        ["slug"],
        unique=False
    )

    op.create_index(
        "ix_organizations_organization_type",
        "organizations",
        ["organization_type"],
        unique=False
    )

    op.create_index(
        "ix_organizations_status",
        "organizations",
        ["status"],
        unique=False
    )

    #
    # WORKSPACES
    #

    op.create_table(
        "workspaces",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "organization_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "code",
            sa.String(length=100),
            nullable=False
        ),

        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False
        ),

        sa.Column(
            "slug",
            sa.String(length=255),
            nullable=False
        ),

        sa.Column(
            "description",
            sa.Text(),
            nullable=True
        ),

        sa.Column(
            "icon_url",
            sa.String(length=1000),
            nullable=True
        ),

        sa.Column(
            "is_system",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False
        ),

        sa.Column(
            "is_public",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False
        ),

        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False
        ),

        sa.Column(
            "created_by_user_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False
        ),

        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_workspace_organization_id"
        ),

        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
            name="fk_workspace_created_by_user_id"
        ),

        sa.PrimaryKeyConstraint(
            "id"
        ),

        sa.UniqueConstraint(
            "organization_id",
            "code",
            name="uq_workspace_organization_code"
        ),

        sa.UniqueConstraint(
            "organization_id",
            "slug",
            name="uq_workspace_organization_slug"
        ),
    )

    op.create_index(
        "ix_workspaces_id",
        "workspaces",
        ["id"],
        unique=False
    )

    op.create_index(
        "ix_workspaces_organization_id",
        "workspaces",
        ["organization_id"],
        unique=False
    )

    op.create_index(
        "ix_workspaces_code",
        "workspaces",
        ["code"],
        unique=False
    )

    op.create_index(
        "ix_workspaces_slug",
        "workspaces",
        ["slug"],
        unique=False
    )

    op.create_index(
        "ix_workspaces_created_by_user_id",
        "workspaces",
        ["created_by_user_id"],
        unique=False
    )


def downgrade() -> None:

    #
    # Reverse dependency order:
    # workspaces -> organizations
    #

    op.drop_index(
        "ix_workspaces_created_by_user_id",
        table_name="workspaces"
    )

    op.drop_index(
        "ix_workspaces_slug",
        table_name="workspaces"
    )

    op.drop_index(
        "ix_workspaces_code",
        table_name="workspaces"
    )

    op.drop_index(
        "ix_workspaces_organization_id",
        table_name="workspaces"
    )

    op.drop_index(
        "ix_workspaces_id",
        table_name="workspaces"
    )

    op.drop_table(
        "workspaces"
    )

    op.drop_index(
        "ix_organizations_status",
        table_name="organizations"
    )

    op.drop_index(
        "ix_organizations_organization_type",
        table_name="organizations"
    )

    op.drop_index(
        "ix_organizations_slug",
        table_name="organizations"
    )

    op.drop_index(
        "ix_organizations_code",
        table_name="organizations"
    )

    op.drop_index(
        "ix_organizations_id",
        table_name="organizations"
    )

    op.drop_table(
        "organizations"
    )