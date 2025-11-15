from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.rid import generate_rid
from app.models.goal.user_goals import UserGoal
from app.models.metric.body.composition import BodyComposition
from app.repositories.user_goals_repository import UserGoalRepository
from app.schemas.goal.user_goals import (
    GoalTargetParam,
    GoalTargetType,
    GoalVariantBuildResult,
    UserGoalCreateRequest,
    UserGoalParams,
)
from app.schemas.goal.templates import GoalTemplateRead
from app.schemas.profile.user_profile import UserProfileRead
from app.services.goal_template_service import GoalTemplateService
from app.services.macro_preset_service import MacroPresetService
from app.services.user_profile_service import UserProfileService


class UserGoalService:
    """Business logic around user_goals records."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = UserGoalRepository(db)
        self.template_service = GoalTemplateService(db)
        self.profile_service = UserProfileService(db)
        self.macro_service = MacroPresetService()


    """CRUD methods"""
    def get_active_goal(self, user_id: str) -> Optional[UserGoal]:
        """Return the currently active goal for a user."""
        return self.repository.get_active_for_user(user_id)

    def list_goals(self, user_id: str) -> List[UserGoal]:
        """Return all goals for a user newest first."""
        return self.repository.list_for_user(user_id)

    def delete_goal(self, goal_id: str) -> Optional[UserGoal]:
        """Hard delete a user goal (admin/testing)."""
        goal = self.repository.get_by_id(goal_id)
        if not goal:
            return None
        return self.repository.delete(goal)


    def create_goal(
        self,
        user_id: str,
        request: UserGoalCreateRequest,
    ) -> UserGoal:
        """Create a new goal by combining template defaults, profile data, and client params."""
        template = self._get_template_or_raise(request.template_slug)
        profile = self._get_profile_or_raise(user_id)
        pace_key = request.pace_mode.value
        pace_defaults = template.defaults.pace_modes.get(pace_key)
        if pace_defaults is None:
            raise ValueError(f"Pace mode '{pace_key}' is not supported by template {template.slug}")

        params = self._build_goal_params(request, template, pace_defaults.weekly_rate_pct_bw)
        build_result = self._build_variants(user_id, template, profile, params)
        now = datetime.now(timezone.utc)

        # Ensure only one goal stays active
        self.deactivate_active_goal(user_id, ended_at=now)

        goal = UserGoal(
            id=generate_rid("goal", "user"),
            user_id=user_id,
            template_slug=template.slug,
            template_version=template.version,
            params=params.model_dump(),
            variants=build_result.variants.model_dump(),
            variants_basis=build_result.variants_basis.value,
            variants_version=build_result.variants_version,
            variants_updated_at=now,
            start_weight_lb=build_result.start_weight_lb,
            start_bmi=build_result.start_bmi,
            active=True,
        )
        return self.repository.create(goal)

    """Helper methods for create_goal"""

    def _get_template_or_raise(self, slug: str) -> GoalTemplateRead:
        template = self.template_service.get_latest_active(slug)
        if not template:
            raise ValueError(f"Template '{slug}' not found or inactive")
        return template

    def _get_profile_or_raise(self, user_id: str) -> UserProfileRead:
        profile = self.profile_service.get_profile(user_id)
        if not profile:
            raise ValueError("User profile is required before creating a goal")
        return UserProfileRead.model_validate(profile)

    def _build_goal_params(
        self,
        request: UserGoalCreateRequest,
        template: GoalTemplateRead,
        weekly_rate_pct: float,
    ) -> UserGoalParams:
        target = template.defaults.default_target
        goal_target = None
        if target is not None:
            try:
                target_type = GoalTargetType(target.type)
            except ValueError:
                target_type = GoalTargetType.NONE
            goal_target = GoalTargetParam(type=target_type, value=target.value)

        return UserGoalParams(
            pace_mode=request.pace_mode,
            weekly_rate_target_pct=weekly_rate_pct,
            target=goal_target,
            protein_rule=template.defaults.protein_rule_default,
            training_days_per_week=None,
            activity_override=None,
        )

    def _build_variants(
        self,
        user_id: str,
        template: GoalTemplateRead,
        profile: UserProfileRead,
        params: UserGoalParams,
    ) -> GoalVariantBuildResult:
        """Delegate to macro service for preset generation."""
        latest_weight = self._get_latest_weight_lb(user_id)
        return self.macro_service.build_presets(
            template=template,
            profile=profile,
            params=params,
            latest_weight_lb=latest_weight,
        )

    def deactivate_active_goal(self, user_id: str, ended_at: datetime) -> None:
        """Deactivate the currently active goal for a user, if one exists."""
        self.repository.deactivate_active_goal(user_id, ended_at)

    def _get_latest_weight_lb(self, user_id: str) -> Optional[float]:
        record = (
            self.db.query(BodyComposition)
            .filter(
                BodyComposition.user_id == user_id,
                BodyComposition.weight.isnot(None),
            )
            .order_by(BodyComposition.date_hour.desc())
            .first()
        )
        if not record or record.weight is None:
            return None
        return float(record.weight)
