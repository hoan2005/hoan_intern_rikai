"""Add role column to users table.

Revision ID: 20261120_01
Revises: 20261113_01
Create Date: 2026-11-20
"""

from alembic import op
import sqlalchemy as sa

revision = "20261120_01"
down_revision = "20261113_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add role column with a server default of 'user' so existing rows
    # get the value automatically. The default is removed afterwards
    # but the column remains with the default value.
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(20),
            nullable=False,
            server_default=sa.text("'user'"),
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "role")