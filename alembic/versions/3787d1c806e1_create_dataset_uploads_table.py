"""create dataset uploads table

Revision ID: 3787d1c806e1
Revises: a0f16de552a5
Create Date: 2026-07-16 06:54:05.097539

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3787d1c806e1'
down_revision: Union[str, Sequence[str], None] = 'a0f16de552a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "dataset_uploads",

        sa.Column(
            "id",
            sa.BigInteger(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "dataset_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "original_file_name",
            sa.String(length=500),
            nullable=False,
        ),

        sa.Column(
            "stored_file_name",
            sa.String(length=500),
            nullable=False,
        ),

        sa.Column(
            "file_extension",
            sa.String(length=30),
            nullable=False,
        ),

        sa.Column(
            "mime_type",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "file_size",
            sa.BigInteger(),
            nullable=False,
        ),

        sa.Column(
            "storage_provider",
            sa.String(length=100),
            nullable=False,
        ),

        sa.Column(
            "storage_reference",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "checksum",
            sa.String(length=128),
            nullable=True,
        ),

        sa.Column(
            "upload_status",
            sa.String(length=50),
            nullable=False,
            server_default="UPLOADED",
        ),

        sa.Column(
            "ingestion_status",
            sa.String(length=50),
            nullable=False,
            server_default="PENDING",
        ),

        sa.Column(
            "parser_type",
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            "parser_version",
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            "metadata_json",
            postgresql.JSONB(
                astext_type=sa.Text(),
            ),
            nullable=True,
        ),

        sa.Column(
            "error_message",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "created_by",
            sa.String(length=255),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
        ),

        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ["dataset_id"],
            ["datasets.id"],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint(
            "id",
        ),

        sa.UniqueConstraint(
            "stored_file_name",
        ),
    )

    op.create_index(
        op.f(
            "ix_dataset_uploads_dataset_id",
        ),
        "dataset_uploads",
        ["dataset_id"],
        unique=False,
    )

def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f(
            "ix_dataset_uploads_dataset_id",
        ),
        table_name="dataset_uploads",
    )

    op.drop_table(
        "dataset_uploads",
    )