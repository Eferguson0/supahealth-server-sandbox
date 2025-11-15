from enum import Enum
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


"""Helper enums"""

class GoalPaceMode(str, Enum):
    CONSERVATIVE = "conservative"
    STANDARD = "standard"
    AGGRESSIVE = "aggressive"


class GoalTargetType(str, Enum):
    BMI = "bmi"
    WEIGHT_LB = "weight_lb"
    PERCENT_LOSS = "percent_loss"
    NONE = "none"
    TIMELINE_WEEKS = "timeline_weeks"


class GoalVariantBasis(str, Enum):
    NONE = "none"
    REST = "rest"
    WORKOUT = "workout"


"""API Request schemas"""

class UserGoalCreateRequest(BaseModel):
    template_slug: str = Field(..., description="Template slug (e.g., lean_defined)")
    pace_mode: GoalPaceMode = Field(..., description="Requested pace mode")


"""Nested model schemas"""

class GoalTargetParam(BaseModel):
    type: GoalTargetType = Field(
        ..., description="Goal target type (e.g., bmi, weight_lb, timeline_weeks)"
    )
    value: Optional[float] = Field(
        None,
        description="Numeric target value when applicable (weeks, pounds, etc.)",
    )


"""Base model schemas"""

class UserGoalParams(BaseModel):
    pace_mode: GoalPaceMode = Field(
        ..., description="Selected pace mode (conservative|standard|aggressive)"
    )
    weekly_rate_target_pct: Optional[float] = Field(
        None, description="Percent bodyweight change per week"
    )
    target: Optional[GoalTargetParam] = None
    protein_rule: Optional[str] = Field(
        None, description="Protein rule identifier (e.g., 0.9*g_per_lb_bw)"
    )
    training_days_per_week: Optional[int] = Field(
        None, description="Captured for future features; unused in v1"
    )
    activity_override: Optional[str] = Field(
        None, description="Optional override for PAL/activity level"
    )


class GoalVariantPreset(BaseModel):
    calories_kcal: float
    protein_g: float
    fat_g: float
    carbs_g: float
    tdee_kcal_est: float
    delta_kcal: float
    algo: str
    version: int


class GoalVariants(BaseModel):
    """Computed presets keyed by variant name (rest/workout)."""

    rest: GoalVariantPreset
    workout: GoalVariantPreset



class UserGoalRead(BaseModel):
    id: str
    user_id: str
    template_slug: str
    template_version: int
    params: UserGoalParams
    variants: GoalVariants
    variants_basis: GoalVariantBasis
    variants_version: int
    variants_updated_at: datetime
    start_weight_lb: Optional[float]
    start_bmi: Optional[float]
    active: bool
    created_at: datetime
    ended_at: Optional[datetime]

    class Config:
        from_attributes = True


class GoalVariantBuildResult(BaseModel):
    variants: GoalVariants
    variants_basis: GoalVariantBasis
    variants_version: int = 1
    start_weight_lb: Optional[float] = None
    start_bmi: Optional[float] = None
