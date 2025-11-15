from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func, text

from app.db.session import Base


class UserGoal(Base):
    __tablename__ = "user_goals"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(
        String,
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        nullable=False,
    )
    template_slug = Column(Text, nullable=False)
    template_version = Column(Integer, nullable=False)
    params = Column(JSONB, nullable=False)
    variants = Column(JSONB, nullable=False)
    variants_basis = Column(Text, nullable=False, server_default=text("'workout'"))
    variants_version = Column(Integer, nullable=False, server_default=text("1"))
    variants_updated_at = Column(DateTime(timezone=True), nullable=False)
    start_weight_lb = Column(Numeric(6, 2), nullable=True)
    start_bmi = Column(Numeric(5, 2), nullable=True)
    active = Column(Boolean, nullable=False, server_default=text("true"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["template_slug", "template_version"],
            ["goal_templates.slug", "goal_templates.version"],
            name="fk_user_goals_template",
        ),
        CheckConstraint(
            "variants_basis in ('none','rest','workout')",
            name="ck_user_goals_variants_basis",
        ),
        Index(
            "uq_user_goals_active_per_user",
            user_id,
            unique=True,
            postgresql_where=active.is_(True),
        ),
        Index(
            "ix_user_goals_template_version",
            template_slug,
            template_version,
        ),
    )
