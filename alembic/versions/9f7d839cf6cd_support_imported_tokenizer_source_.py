"""support imported tokenizer source lineage

Revision ID: 9f7d839cf6cd
Revises: f928bff94090
Create Date: 2026-07-10 06:22:42.315457

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f7d839cf6cd'
down_revision: Union[str, Sequence[str], None] = 'f928bff94090'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "tokenizer_versions",
        "tokenizer_training_job_id",
        existing_type=sa.Integer(),
        nullable=True,
    )

    op.add_column(
        "tokenizer_versions",
        sa.Column(
            "source_type",
            sa.String(),
            nullable=True,
        ),
    )

    op.add_column(
        "tokenizer_versions",
        sa.Column(
            "source_uri",
            sa.String(),
            nullable=True,
        ),
    )

    op.add_column(
        "tokenizer_versions",
        sa.Column(
            "source_revision",
            sa.String(),
            nullable=True,
        ),
    )

    op.create_check_constraint(
        "ck_tokenizer_versions_valid_lineage",
        "tokenizer_versions",
        """
        (
            tokenizer_training_job_id IS NOT NULL
        )
        OR
        (
            source_type IS NOT NULL
            AND btrim(source_type) <> ''
            AND source_uri IS NOT NULL
            AND btrim(source_uri) <> ''
            AND source_revision IS NOT NULL
            AND btrim(source_revision) <> ''
        )
        """,
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_tokenizer_versions_valid_lineage",
        "tokenizer_versions",
        type_="check",
    )

    op.drop_column(
        "tokenizer_versions",
        "source_revision",
    )

    op.drop_column(
        "tokenizer_versions",
        "source_uri",
    )

    op.drop_column(
        "tokenizer_versions",
        "source_type",
    )

    op.alter_column(
        "tokenizer_versions",
        "tokenizer_training_job_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
