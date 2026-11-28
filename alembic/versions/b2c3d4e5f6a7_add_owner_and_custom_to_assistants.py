"""add owner_user_id and is_custom to assistants for My Mini AI

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-11-27 17:15:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "assistants",
        sa.Column("owner_user_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "assistants",
        sa.Column(
            "is_custom",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.create_foreign_key(
        "fk_assistants_owner_user_id",
        "assistants",
        "users",
        ["owner_user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(
        "ix_assistants_owner_user_id",
        "assistants",
        ["owner_user_id"],
        unique=False,
    )
    for tbl in (
        "assistants",
        "assistant_configs",
        "knowledge_bases",
        "assistant_knowledge_bases",
        "knowledge_base_documents",
        "documents",
    ):
        op.execute(
            f"SELECT setval(pg_get_serial_sequence('{tbl}', 'id'), "
            f"COALESCE((SELECT MAX(id) FROM {tbl}), 0) + 1, false)"
        )


def downgrade():
    op.drop_index("ix_assistants_owner_user_id", table_name="assistants")
    op.drop_constraint("fk_assistants_owner_user_id", "assistants", type_="foreignkey")
    op.drop_column("assistants", "is_custom")
    op.drop_column("assistants", "owner_user_id")
