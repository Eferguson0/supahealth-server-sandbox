from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.goal.user_goals import UserGoal


class UserGoalRepository:
    """CRUD helpers for the user_goals table."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, goal_id: str) -> Optional[UserGoal]:
        return self.db.query(UserGoal).filter(UserGoal.id == goal_id).one_or_none()

    def get_active_for_user(self, user_id: str) -> Optional[UserGoal]:
        return (
            self.db.query(UserGoal)
                .filter(UserGoal.user_id == user_id, UserGoal.active.is_(True))
                .one_or_none()
        )

    def list_for_user(self, user_id: str) -> list[UserGoal]:
        return (
            self.db.query(UserGoal)
                .filter(UserGoal.user_id == user_id)
                .order_by(UserGoal.created_at.desc())
                .all()
        )

    def create(self, goal: UserGoal) -> UserGoal:
        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def update(self, goal: UserGoal) -> UserGoal:
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def delete(self, goal: UserGoal) -> UserGoal:
        self.db.delete(goal)
        self.db.commit()
        return goal

    def deactivate_active_goal(self, user_id: str, ended_at: datetime) -> None:
        """Deactivate the currently active goal for a user, if one exists."""
        existing = self.get_active_for_user(user_id)
        if existing:
            existing.active = False
            existing.ended_at = ended_at
            self.update(existing)