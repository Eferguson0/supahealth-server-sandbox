from typing import Optional

from sqlalchemy.orm import Session

from app.models.profile.user_profile import UserProfile


class UserProfileRepository:
    """Data access helpers for user profile records."""

    def __init__(self, db: Session):
        self.db = db

    def get(self, user_id: str) -> Optional[UserProfile]:
        """Fetch the profile for a given user, if it exists."""
        return (
            self.db.query(UserProfile)
            .filter(UserProfile.user_id == user_id)
            .one_or_none()
        )

    def create(self, profile: UserProfile) -> UserProfile:
        """Persist a brand new profile row."""
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def update(self, profile: UserProfile) -> UserProfile:
        """Flush in-memory changes for an existing profile."""
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def delete(self, user_id: str) -> Optional[UserProfile]:
        """Remove the profile; returns the deleted row for auditing."""
        profile = self.get(user_id)
        if not profile:
            return None

        self.db.delete(profile)
        self.db.commit()
        return profile
