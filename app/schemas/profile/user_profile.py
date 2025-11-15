from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


"""Core schema"""

class UserProfileBase(BaseModel):
    height_in: float = Field(..., gt=0, description="User height in inches")
    birth_date: date = Field(..., description="Birth date (used for age calculations)")
    sex: str = Field(..., pattern="^(masc|fem|other)$")
    timezone: str = Field(..., description="IANA timezone (e.g., America/Los_Angeles)")
    default_activity_level: str = Field(
        "moderate", description="Fallback PAL when no activity override exists"
    )


"""API Request schemas"""

class UserProfileCreate(UserProfileBase):
    user_id: str = Field(..., description="Auth user ID (FK)")


class UserProfileUpdate(BaseModel):
    height_in: Optional[float] = Field(None, gt=0)
    birth_date: Optional[date] = None
    sex: Optional[str] = Field(None, pattern="^(masc|fem|other)$")
    timezone: Optional[str] = None
    default_activity_level: Optional[str] = None


"""API Response schemas"""

class UserProfileRead(UserProfileBase):
    user_id: str

    class Config:
        from_attributes = True


class UserProfileDeleteResponse(BaseModel):
    message: str = "Profile deleted"
    deleted: bool = True
