"""create user goals table

Revision ID: e520ac8236d9
Revises: 5178a082305f
Create Date: 2025-11-11 13:48:34.476828

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'e520ac8236d9'
down_revision: Union[str, Sequence[str], None] = '5178a082305f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "user_goals",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("template_slug", sa.Text(), nullable=False),
        sa.Column("template_version", sa.Integer(), nullable=False),
        sa.Column("params", sa.dialects.postgresql.JSONB(), nullable=False),
        sa.Column("variants", sa.dialects.postgresql.JSONB(), nullable=False),
        sa.Column(
            "variants_basis",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'workout'"),
        ),
        sa.Column(
            "variants_version",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1"),
        ),
        sa.Column("variants_updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("start_weight_lb", sa.Numeric(6, 2), nullable=True),
        sa.Column("start_bmi", sa.Numeric(5, 2), nullable=True),
        sa.Column(
            "active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "variants_basis in ('none','rest','workout')",
            name="ck_user_goals_variants_basis",
        ),
        sa.ForeignKeyConstraint(
            ["template_slug", "template_version"],
            ["goal_templates.slug", "goal_templates.version"],
            name="fk_user_goals_template",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["auth_users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_user_goals_active_per_user",
        "user_goals",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("active = true"),
    )
    op.create_index(
        "ix_user_goals_template_version",
        "user_goals",
        ["template_slug", "template_version"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_user_goals_template_version", table_name="user_goals")
    op.drop_index("uq_user_goals_active_per_user", table_name="user_goals")
    op.drop_table("user_goals")
