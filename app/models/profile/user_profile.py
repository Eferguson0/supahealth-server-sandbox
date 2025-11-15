from sqlalchemy import CheckConstraint, Column, Date, ForeignKey, Numeric, String, Text
from sqlalchemy.sql import text

from app.db.session import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id = Column(
        String,
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    height_in = Column(Numeric(5, 2), nullable=False)
    birth_date = Column(Date, nullable=False)
    sex = Column(
        Text,
        nullable=False,
    )
    timezone = Column(Text, nullable=False)
    default_activity_level = Column(Text, nullable=False, server_default=text("'moderate'"))

    __table_args__ = (
        CheckConstraint(
            "sex in ('masc','fem','other')",
            name="ck_user_profiles_sex",
        ),
    )
