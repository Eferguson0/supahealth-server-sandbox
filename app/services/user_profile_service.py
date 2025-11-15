from typing import Optional

from sqlalchemy.orm import Session

from app.models.profile.user_profile import UserProfile
from app.repositories.user_profile_repository import UserProfileRepository
from app.schemas.profile.user_profile import (
    UserProfileBase,
    UserProfileUpdate,
)


class UserProfileService:
    """Thin wrapper around the profile repository for future business logic."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = UserProfileRepository(db)

    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """Return the user's profile row if it exists."""
        return self.repository.get(user_id)

    def create_profile(self, user_id: str, payload: UserProfileBase) -> UserProfile:
        """Persist a new profile (validation handled by Pydantic)."""
        profile = UserProfile(user_id=user_id, **payload.model_dump())
        return self.repository.create(profile)

    def update_profile(
        self, user_id: str, payload: UserProfileUpdate
    ) -> Optional[UserProfile]:
        """Apply partial updates to an existing profile."""
        profile = self.repository.get(user_id)
        if not profile:
            return None

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)

        return self.repository.update(profile)

    def delete_profile(self, user_id: str) -> Optional[UserProfile]:
        """Remove a user's profile."""
        return self.repository.delete(user_id)
