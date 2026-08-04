"""add runtime components to training providers

Revision ID: fe7c4e8b3b38
Revises: aa2f92e9fb0c
Create Date: 2026-07-23 13:10:20.232484

"""
from alembic import op
import sqlalchemy as sa

revision = "<new_revision>"
down_revision = "aa2f92e9fb0c"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "training_providers",
        sa.Column(
            "runtime_components",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'::json"),
        ),
    )


def downgrade():
    op.drop_column(
        "training_providers",
        "runtime_components",
    )