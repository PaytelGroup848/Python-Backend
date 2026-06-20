"""migrate models to provider architecture

Revision ID: 5fb5c4bfee2e
Revises: 95d83ce39bc4
Create Date: 2026-06-18 05:21:38.342803
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5fb5c4bfee2e"
down_revision: Union[str, Sequence[str], None] = "95d83ce39bc4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # ==========================================
    # STEP 1: ADD NEW COLUMNS (NULLABLE)
    # ==========================================

    op.add_column(
        "models",
        sa.Column(
            "provider_id",
            sa.Integer(),
            nullable=True
        )
    )

    op.add_column(
        "models",
        sa.Column(
            "code",
            sa.String(100),
            nullable=True
        )
    )

    op.add_column(
        "models",
        sa.Column(
            "display_name",
            sa.String(255),
            nullable=True
        )
    )

    # ==========================================
    # STEP 2: FOREIGN KEY
    # ==========================================

    op.create_foreign_key(
        "fk_models_provider_id",
        "models",
        "providers",
        ["provider_id"],
        ["id"]
    )

    # ==========================================
    # STEP 3: MIGRATE EXISTING DATA
    # ==========================================

    op.execute("""
        UPDATE models
        SET provider_id = (
            SELECT id
            FROM providers
            WHERE LOWER(providers.code)
            = LOWER(models.provider)
        )
    """)

    op.execute("""
        UPDATE models
        SET code = model_name
    """)

    op.execute("""
        UPDATE models
        SET display_name = model_name
    """)

    # ==========================================
    # STEP 4: MAKE NOT NULL
    # ==========================================

    op.alter_column(
        "models",
        "provider_id",
        nullable=False
    )

    op.alter_column(
        "models",
        "code",
        nullable=False
    )

    op.alter_column(
        "models",
        "display_name",
        nullable=False
    )

    # ==========================================
    # STEP 5: UNIQUE CONSTRAINT
    # ==========================================

    op.create_unique_constraint(
        "uq_models_code",
        "models",
        ["code"]
    )

    # ==========================================
    # STEP 6: DROP OLD COLUMNS
    # ==========================================

    op.drop_column(
        "models",
        "provider"
    )

    op.drop_column(
        "models",
        "model_name"
    )


def downgrade() -> None:

    op.add_column(
        "models",
        sa.Column(
            "model_name",
            sa.String(),
            nullable=True
        )
    )

    op.add_column(
        "models",
        sa.Column(
            "provider",
            sa.String(),
            nullable=True
        )
    )

    op.execute("""
        UPDATE models
        SET model_name = code
    """)

    op.alter_column(
        "models",
        "model_name",
        nullable=False
    )

    op.alter_column(
        "models",
        "provider",
        nullable=False
    )

    op.drop_constraint(
        "uq_models_code",
        "models",
        type_="unique"
    )

    op.drop_constraint(
        "fk_models_provider_id",
        "models",
        type_="foreignkey"
    )

    op.drop_column(
        "models",
        "provider_id"
    )

    op.drop_column(
        "models",
        "code"
    )

    op.drop_column(
        "models",
        "display_name"
    )