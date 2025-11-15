import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.auth.user import AuthUser
from app.schemas.profile.user_profile import (
    UserProfileBase,
    UserProfileDeleteResponse,
    UserProfileRead,
    UserProfileUpdate,
)
from app.services.auth_service import get_current_active_user
from app.services.user_profile_service import UserProfileService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user/profile", tags=["user-profile"])


@router.get(
    "/",
    response_model=UserProfileRead,
    summary="Get the current user's profile",
    description="Returns the stored profile inputs for the authenticated user.",
    responses={
        200: {"description": "Profile retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "Profile not found"},
    },
)
async def get_user_profile(
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
) -> UserProfileRead:
    service = UserProfileService(db)
    profile = service.get_profile(current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    logger.info("Retrieved profile for %s", current_user.id)
    return profile


@router.post(
    "/",
    response_model=UserProfileRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create the current user's profile",
    description="Creates a profile for the authenticated user.",
    responses={
        201: {"description": "Profile created"},
        400: {"description": "Profile already exists"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
    },
)
async def create_user_profile(
    payload: UserProfileBase,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
) -> UserProfileRead:
    service = UserProfileService(db)
    existing = service.get_profile(current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists",
        )

    logger.info("Creating profile for %s", current_user.id)
    return service.create_profile(current_user.id, payload)


@router.patch(
    "/",
    response_model=UserProfileRead,
    summary="Update the current user's profile",
    description="Partially updates the stored profile inputs.",
    responses={
        200: {"description": "Profile updated"},
        400: {"description": "No fields provided"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "Profile not found"},
    },
)
async def update_user_profile(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
) -> UserProfileRead:
    service = UserProfileService(db)
    profile = service.get_profile(current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    """Empty payload check"""
    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )
    logger.info(
        "Updated profile for %s with fields %s",
        current_user.id,
        list(update_data.keys()),
    )
    updated_profile = service.update_profile(current_user.id, payload)
    if not updated_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    return updated_profile


@router.delete(
    "/",
    response_model=UserProfileDeleteResponse,
    summary="Delete the current user's profile",
    description="Removes the stored profile inputs (primarily for testing/resets).",
    responses={
        200: {"description": "Profile deleted"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "Profile not found"},
    },
)
async def delete_user_profile(
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
) -> UserProfileDeleteResponse:
    service = UserProfileService(db)
    deleted = service.delete_profile(current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    logger.info("Deleted profile for %s", current_user.id)
    return UserProfileDeleteResponse()
