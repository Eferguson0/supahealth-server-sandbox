"""add user profiles table

Revision ID: 5178a082305f
Revises: abbf00aafb66
Create Date: 2025-11-10 16:35:20.946652

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '5178a082305f'
down_revision: Union[str, Sequence[str], None] = 'abbf00aafb66'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "user_profiles",
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("height_in", sa.Numeric(5, 2), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=False),
        sa.Column("sex", sa.Text(), nullable=False),
        sa.Column("timezone", sa.Text(), nullable=False),
        sa.Column(
            "default_activity_level",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'moderate'"),
        ),
        sa.CheckConstraint(
            "sex in ('masc','fem','other')",
            name="ck_user_profiles_sex",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["auth_users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("user_profiles")
