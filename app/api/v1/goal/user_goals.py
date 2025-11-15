import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.auth.user import AuthUser
from app.schemas.goal.user_goals import UserGoalCreateRequest, UserGoalRead
from app.services.auth_service import get_current_active_user
from app.services.user_goals_service import UserGoalService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user-goals", tags=["user-goals"])


@router.get(
    "/active",
    response_model=UserGoalRead,
    summary="Get the active goal for the current user",
    responses={
        200: {"description": "Active goal retrieved"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "No active goal"},
    },
)
async def get_active_goal(
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    goal_service = UserGoalService(db)
    goal = goal_service.get_active_goal(current_user.id)
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active goal")
    return goal


@router.get(
    "/",
    response_model=List[UserGoalRead],
    summary="List all goals for the current user",
    responses={
        200: {"description": "List of goals retrieved"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "No goals found"},
    },
)
async def list_goals(
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    goal_service = UserGoalService(db)
    return goal_service.list_goals(current_user.id)


@router.post(
    "/",
    response_model=UserGoalRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new goal for the current user",
    responses={
        201: {"description": "Goal created successfully"},
        400: {"description": "Invalid request payload"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        500: {"description": "Internal server error"},
    },
)
async def create_goal(
    payload: UserGoalCreateRequest,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    goal_service = UserGoalService(db)
    try:
        return goal_service.create_goal(current_user.id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.delete(
    "/{goal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a goal (testing/admin)",
    responses={
        204: {"description": "Goal deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "Goal not found"},
        500: {"description": "Internal server error"},
    },
)
async def delete_goal(
    goal_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    goal_service = UserGoalService(db)
    goal = goal_service.repository.get_by_id(goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    goal_service.delete_goal(goal_id)
