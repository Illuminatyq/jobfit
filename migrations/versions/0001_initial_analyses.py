"""initial analyses table

Revision ID: 0001
Revises:
Create Date: 2026-11-21
"""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "analyses",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("vacancy_text", sa.Text(), nullable=False),
        sa.Column("profile_text", sa.Text(), nullable=False),
        sa.Column("coverage", sa.Integer(), nullable=False),
        sa.Column("taxonomy_version", sa.String(length=32), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("analyses")
