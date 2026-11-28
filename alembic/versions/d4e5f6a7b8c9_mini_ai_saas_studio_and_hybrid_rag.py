"""Mini AI SaaS Studio, Hybrid RAG tsvector, Leads, and Knowledge Gaps

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-11-28 12:35:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "d4e5f6a7b8c9"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def upgrade():
    # 1. Extend assistants for public share, strict grounding, and embed domain allowlist
    op.add_column("assistants", sa.Column("share_slug", sa.String(length=64), nullable=True))
    op.add_column(
        "assistants",
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column(
        "assistants",
        sa.Column("strict_rag", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column(
        "assistants",
        sa.Column("allowed_domains", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column("assistants", sa.Column("welcome_message", sa.Text(), nullable=True))
    op.create_index("ix_assistants_share_slug", "assistants", ["share_slug"], unique=True)

    # 2. Add generated tsvector + GIN index to documents for fast BM25 keyword search
    op.execute(
        "ALTER TABLE documents "
        "ADD COLUMN IF NOT EXISTS content_tsv tsvector "
        "GENERATED ALWAYS AS (to_tsvector('simple', coalesce(content, ''))) STORED"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_documents_content_tsv "
        "ON documents USING gin (content_tsv)"
    )

    # 3. Create mini_ai_leads
    op.create_table(
        "mini_ai_leads",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("assistant_id", sa.Integer(), nullable=False),
        sa.Column("owner_user_id", sa.Integer(), nullable=False),
        sa.Column("visitor_name", sa.String(length=120), nullable=False),
        sa.Column("visitor_contact", sa.String(length=160), nullable=False),
        sa.Column("first_question", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["assistant_id"],
            ["assistants.id"],
            name="fk_mini_ai_leads_assistant_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["owner_user_id"],
            ["users.id"],
            name="fk_mini_ai_leads_owner_user_id",
            ondelete="CASCADE",
        ),
    )
    op.create_index("ix_mini_ai_leads_assistant_id", "mini_ai_leads", ["assistant_id"])
    op.create_index("ix_mini_ai_leads_owner_user_id", "mini_ai_leads", ["owner_user_id"])
    op.create_index(
        "ix_mini_ai_leads_assistant_created",
        "mini_ai_leads",
        ["assistant_id", "created_at"],
    )

    # 4. Create mini_ai_gaps with partial unique index for atomic deduplication
    op.create_table(
        "mini_ai_gaps",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("assistant_id", sa.Integer(), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("normalized_question", sa.Text(), nullable=False),
        sa.Column("hit_count", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("resolved", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["assistant_id"],
            ["assistants.id"],
            name="fk_mini_ai_gaps_assistant_id",
            ondelete="CASCADE",
        ),
    )
    op.create_index("ix_mini_ai_gaps_assistant_id", "mini_ai_gaps", ["assistant_id"])
    op.create_index(
        "ix_mini_ai_gaps_assistant_resolved",
        "mini_ai_gaps",
        ["assistant_id", "resolved"],
    )
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_mini_ai_gaps_unresolved "
        "ON mini_ai_gaps (assistant_id, md5(normalized_question)) "
        "WHERE resolved = false"
    )


def downgrade():
    op.execute("DROP INDEX IF EXISTS uq_mini_ai_gaps_unresolved")
    op.drop_index("ix_mini_ai_gaps_assistant_resolved", table_name="mini_ai_gaps")
    op.drop_index("ix_mini_ai_gaps_assistant_id", table_name="mini_ai_gaps")
    op.drop_table("mini_ai_gaps")

    op.drop_index("ix_mini_ai_leads_assistant_created", table_name="mini_ai_leads")
    op.drop_index("ix_mini_ai_leads_owner_user_id", table_name="mini_ai_leads")
    op.drop_index("ix_mini_ai_leads_assistant_id", table_name="mini_ai_leads")
    op.drop_table("mini_ai_leads")

    op.execute("DROP INDEX IF EXISTS ix_documents_content_tsv")
    op.execute("ALTER TABLE documents DROP COLUMN IF EXISTS content_tsv")

    op.drop_index("ix_assistants_share_slug", table_name="assistants")
    op.drop_column("assistants", "welcome_message")
    op.drop_column("assistants", "allowed_domains")
    op.drop_column("assistants", "strict_rag")
    op.drop_column("assistants", "is_public")
    op.drop_column("assistants", "share_slug")
