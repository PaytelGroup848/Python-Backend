"""link document jobs to knowledge base documents

Revision ID: be4c89ad1e6a
Revises: ae2009452679
Create Date: 2026-06-18 11:42:07.562394

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "be4c89ad1e6a"
down_revision: Union[str, Sequence[str], None] = "ae2009452679"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.add_column(
        "document_jobs",
        sa.Column(
            "knowledge_base_document_id",
            sa.Integer(),
            nullable=True
        )
    )

    op.create_index(
        "ix_document_jobs_knowledge_base_document_id",
        "document_jobs",
        ["knowledge_base_document_id"],
        unique=False
    )

    op.create_foreign_key(
        "fk_document_jobs_kbd_id",
        "document_jobs",
        "knowledge_base_documents",
        ["knowledge_base_document_id"],
        ["id"]
    )


def downgrade() -> None:

    op.drop_constraint(
        "fk_document_jobs_kbd_id",
        "document_jobs",
        type_="foreignkey"
    )

    op.drop_index(
        "ix_document_jobs_knowledge_base_document_id",
        table_name="document_jobs"
    )

    op.drop_column(
        "document_jobs",
        "knowledge_base_document_id"
    )