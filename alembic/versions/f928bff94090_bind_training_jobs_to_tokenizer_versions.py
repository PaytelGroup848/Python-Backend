"""bind training jobs to tokenizer versions

Revision ID: f928bff94090
Revises: 4135892e0366
Create Date: 2026-07-08 12:50:06.018103
"""

from typing import (
    Sequence,
    Union,
)

from alembic import op
import sqlalchemy as sa


revision: str = "f928bff94090"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "4135892e0366"

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
        "training_jobs",
        sa.Column(
            "tokenizer_version_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_index(
        op.f(
            "ix_training_jobs_tokenizer_version_id"
        ),
        "training_jobs",
        [
            "tokenizer_version_id",
        ],
        unique=False,
    )

    op.create_foreign_key(
        "fk_training_job_tokenizer_version_id",
        "training_jobs",
        "tokenizer_versions",
        [
            "tokenizer_version_id",
        ],
        [
            "id",
        ],
        ondelete="RESTRICT",
    )


def downgrade() -> None:

    op.drop_constraint(
        "fk_training_job_tokenizer_version_id",
        "training_jobs",
        type_="foreignkey",
    )

    op.drop_index(
        op.f(
            "ix_training_jobs_tokenizer_version_id"
        ),
        table_name="training_jobs",
    )

    op.drop_column(
        "training_jobs",
        "tokenizer_version_id",
    )