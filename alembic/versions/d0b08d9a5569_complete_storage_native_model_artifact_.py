"""complete storage native model artifact lineage

Revision ID: d0b08d9a5569
Revises: 31c9ec050170
Create Date: 2026-07-10 07:47:36.454999

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'd0b08d9a5569'
down_revision: Union[str, Sequence[str], None] = '31c9ec050170'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.alter_column(
        "model_artifacts",
        "artifact_path",
        existing_type=sa.String(length=1000),
        nullable=True,
    )

    op.alter_column(
        "model_artifacts",
        "storage_provider",
        existing_type=sa.String(length=50),
        nullable=True,
        existing_server_default=sa.text(
            "'LOCAL'::character varying"
        ),
    )

    op.alter_column(
        "model_artifacts",
        "metadata_json",
        existing_type=sa.JSON(),
        type_=postgresql.JSONB(
            astext_type=sa.Text()
        ),
        existing_nullable=False,
        existing_server_default=sa.text(
            "'{}'::json"
        ),
        server_default=sa.text(
            "'{}'::jsonb"
        ),
        postgresql_using=(
            "metadata_json::jsonb"
        ),
    )


def downgrade() -> None:

    op.execute(
        """
        UPDATE model_artifacts
        SET artifact_path = storage_reference
        WHERE artifact_path IS NULL
          AND storage_reference IS NOT NULL
        """
    )

    op.execute(
        """
        UPDATE model_artifacts
        SET storage_provider = 'LOCAL'
        WHERE storage_provider IS NULL
        """
    )

    op.alter_column(
        "model_artifacts",
        "metadata_json",
        existing_type=postgresql.JSONB(
            astext_type=sa.Text()
        ),
        type_=sa.JSON(),
        existing_nullable=False,
        existing_server_default=sa.text(
            "'{}'::jsonb"
        ),
        server_default=sa.text(
            "'{}'::json"
        ),
        postgresql_using=(
            "metadata_json::json"
        ),
    )

    op.alter_column(
        "model_artifacts",
        "storage_provider",
        existing_type=sa.String(length=50),
        nullable=False,
        existing_server_default=sa.text(
            "'LOCAL'::character varying"
        ),
    )

    op.alter_column(
        "model_artifacts",
        "artifact_path",
        existing_type=sa.String(length=1000),
        nullable=False,
    )