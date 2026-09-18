"""create guest refund jobs table for durable DLQ recovery

Revision ID: a1b2c3d4e5f6
Revises: <new_revision>
Create Date: 2026-09-18 17:48:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e5f6"
down_revision = "<new_revision>"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "guest_refund_jobs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("guest_user_id", sa.Integer(), nullable=False),
        sa.Column("request_id", sa.String(length=64), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="PENDING"),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("next_attempt_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("locked_at", sa.DateTime(), nullable=True),
        sa.Column("locked_by", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("processed_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("request_id", name="uq_guest_refund_jobs_request_id"),
    )
    op.create_index("ix_guest_refund_jobs_guest_user_id", "guest_refund_jobs", ["guest_user_id"])
    op.create_index("ix_guest_refund_jobs_request_id", "guest_refund_jobs", ["request_id"])
    op.create_index("ix_guest_refund_jobs_status", "guest_refund_jobs", ["status"])
    op.create_index("ix_guest_refund_jobs_next_attempt_at", "guest_refund_jobs", ["next_attempt_at"])


def downgrade():
    op.drop_index("ix_guest_refund_jobs_next_attempt_at", table_name="guest_refund_jobs")
    op.drop_index("ix_guest_refund_jobs_status", table_name="guest_refund_jobs")
    op.drop_index("ix_guest_refund_jobs_request_id", table_name="guest_refund_jobs")
    op.drop_index("ix_guest_refund_jobs_guest_user_id", table_name="guest_refund_jobs")
    op.drop_table("guest_refund_jobs")
