from datetime import date, datetime
from typing import Optional

from app.schemas.goal.user_goals import (
    GoalVariantBasis,
    GoalVariantBuildResult,
    GoalVariantPreset,
    GoalVariants,
    UserGoalParams,
)
from app.schemas.goal.templates import GoalTemplateRead
from app.schemas.profile.user_profile import UserProfileRead


class MacroPresetService:
    """Calculates macro presets (rest/workout) for a goal."""

    PAL_MAP = {
        "sedentary": 1.2,
        "light": 1.375,
        "lightly_active": 1.375,
        "moderate": 1.55,
        "moderately_active": 1.55,
        "active": 1.725,
        "very_active": 1.9,
    }
    CALORIES_PER_LB = 3500
    VARIANTS_VERSION = 1

    def build_presets(
        self,
        template: GoalTemplateRead,
        profile: UserProfileRead,
        params: UserGoalParams,
        latest_weight_lb: Optional[float],
    ) -> GoalVariantBuildResult:
        if latest_weight_lb is None or latest_weight_lb <= 0:
            return self._placeholder(template)

        weight_lb = float(latest_weight_lb)
        tdee = self._estimate_tdee(template, profile, params, weight_lb)
        rest_calories, workout_calories = self._derive_calorie_targets(
            template, params, tdee, weight_lb
        )

        rest_variant = self._build_rest_variant(
            template, params, weight_lb, tdee, rest_calories
        )
        workout_variant = self._build_workout_variant(
            template, weight_lb, tdee, rest_variant, workout_calories
        )

        height_in = float(profile.height_in or 0)
        start_bmi = self._compute_bmi(weight_lb, height_in)

        variants = GoalVariants(rest=rest_variant, workout=workout_variant)
        return GoalVariantBuildResult(
            variants=variants,
            variants_basis=self._resolve_basis(template.defaults.default_variants_basis),
            variants_version=self.VARIANTS_VERSION,
            start_weight_lb=weight_lb,
            start_bmi=start_bmi,
        )

    # --- Calorie helpers ---

    def _estimate_tdee(
        self,
        template: GoalTemplateRead,
        profile: UserProfileRead,
        params: UserGoalParams,
        weight_lb: float,
    ) -> float:
        bmr = self._mifflin_st_jeor(profile, weight_lb)
        pal = self._pal_multiplier(template, profile, params)
        return bmr * pal

    def _mifflin_st_jeor(self, profile: UserProfileRead, weight_lb: float) -> float:
        weight_kg = weight_lb * 0.45359237
        height_cm = float(profile.height_in or 0) * 2.54
        age_years = self._calculate_age(profile.birth_date)
        sex = (profile.sex or "masc").lower()
        if sex == "fem":
            sex_const = -161
        elif sex == "masc":
            sex_const = 5
        else:
            sex_const = -78  # midpoint between masc/fem
        return (10 * weight_kg) + (6.25 * height_cm) - (5 * age_years) + sex_const

    def _pal_multiplier(
        self,
        template: GoalTemplateRead,
        profile: UserProfileRead,
        params: Optional[UserGoalParams],
    ) -> float:
        override = getattr(params, "activity_override", None) if params else None
        candidate = (
            (override or "").lower()
            or (profile.default_activity_level or "").lower()
            or (template.defaults.default_pal or "").lower()
            or (template.defaults.fallback_activity_level or "").lower()
            or "moderate"
        )
        return self.PAL_MAP.get(candidate, 1.55)

    def _derive_calorie_targets(
        self,
        template: GoalTemplateRead,
        params: UserGoalParams,
        tdee: float,
        weight_lb: float,
    ) -> tuple[float, float]:
        weekly_pct = params.weekly_rate_target_pct or 0.0
        delta = (
            weight_lb
            * (weekly_pct / 100.0)
            * self.CALORIES_PER_LB
            / 7.0
        )
        goal_type = (template.defaults.type or "cut").lower()
        sign = -1 if goal_type in {"cut", "fat_loss", "lean"} else 1
        rest_cal = tdee + (sign * delta)
        rest_cal = self._apply_safety(template, tdee, rest_cal, goal_type)

        # TODO: Add workout calories calculation

        workout_delta = template.defaults.workout_delta_kcal or 0.0
        workout_cal = rest_cal + workout_delta
        return rest_cal, workout_cal

    def _apply_safety(
        self,
        template: GoalTemplateRead,
        tdee: float,
        calories: float,
        goal_type: str,
    ) -> float:
        safety = template.defaults.safety
        if goal_type in {"cut", "fat_loss", "lean"}:
            max_pct = safety.max_deficit_pct_tdee or 0.0
            if max_pct > 0:
                max_delta = tdee * max_pct
                actual_delta = max(0.0, tdee - calories)
                if actual_delta > max_delta:
                    calories = tdee - max_delta
            min_cals = safety.min_calories_kcal or 0.0
            if min_cals > 0 and calories < min_cals:
                calories = min_cals
        else:
            max_pct = safety.max_surplus_pct_tdee or 0.0
            if max_pct > 0:
                max_delta = tdee * max_pct
                actual_delta = max(0.0, calories - tdee)
                if actual_delta > max_delta:
                    calories = tdee + max_delta
        return calories

    # --- Macro composition ---

    def _build_rest_variant(
        self,
        template: GoalTemplateRead,
        params: UserGoalParams,
        weight_lb: float,
        tdee: float,
        calories: float,
    ) -> GoalVariantPreset:
        protein_g = self._calculate_protein(weight_lb, params.protein_rule)
        fat_floor = self._fat_floor(template, weight_lb)
        fat_g = fat_floor
        remaining = calories - (protein_g * 4 + fat_g * 9)
        carbs_g = max(remaining / 4, 0.0)
        algo_name = template.defaults.energy_method_default or "mifflin+pal"

        return GoalVariantPreset(
            calories_kcal=calories,
            protein_g=round(protein_g, 1),
            fat_g=round(fat_g, 1),
            carbs_g=round(carbs_g, 1),
            tdee_kcal_est=round(tdee, 1),
            delta_kcal=round(calories - tdee, 1),
            algo=algo_name,
            version=self.VARIANTS_VERSION,
        )

    def _build_workout_variant(
        self,
        template: GoalTemplateRead,
        weight_lb: float,
        tdee: float,
        rest_variant: GoalVariantPreset,
        calories: float,
    ) -> GoalVariantPreset:
        protein_g = rest_variant.protein_g
        fat_g = max(self._fat_floor(template, weight_lb), rest_variant.fat_g)
        remaining = calories - (protein_g * 4 + fat_g * 9)
        carbs_g = max(remaining / 4, 0.0)

        return GoalVariantPreset(
            calories_kcal=calories,
            protein_g=round(protein_g, 1),
            fat_g=round(fat_g, 1),
            carbs_g=round(carbs_g, 1),
            tdee_kcal_est=round(tdee, 1),
            delta_kcal=round(calories - tdee, 1),
            algo=rest_variant.algo,
            version=self.VARIANTS_VERSION,
        )

    # --- Utility helpers ---

    def _calculate_protein(self, weight_lb: float, rule: Optional[str]) -> float:
        multiplier = 1.0
        if rule and "*g_per_lb" in rule:
            try:
                multiplier = float(rule.split("*")[0])
            except ValueError:
                multiplier = 1.0
        return max(weight_lb * multiplier, 0.0)

    def _fat_floor(self, template: GoalTemplateRead, weight_lb: float) -> float:
        floor = template.defaults.fat_min_g_per_lb or 0.3
        return max(weight_lb * floor, 0.0)

    def _compute_bmi(self, weight_lb: float, height_in: float) -> Optional[float]:
        if height_in <= 0:
            return None
        weight_kg = weight_lb * 0.45359237
        height_m = height_in * 0.0254
        bmi = weight_kg / (height_m**2)
        return round(bmi, 1)

    def _calculate_age(self, birth_date: Optional[date]) -> int:
        if not birth_date:
            return 0
        today = datetime.utcnow().date()
        age = today.year - birth_date.year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        return max(age, 0)

    def _placeholder(self, template: GoalTemplateRead) -> GoalVariantBuildResult:
        base = GoalVariantPreset(
            calories_kcal=0.0,
            protein_g=0.0,
            fat_g=0.0,
            carbs_g=0.0,
            tdee_kcal_est=0.0,
            delta_kcal=0.0,
            algo=f"{template.slug}-placeholder",
            version=self.VARIANTS_VERSION,
        )
        workout = GoalVariantPreset(**base.model_dump())
        return GoalVariantBuildResult(
            variants=GoalVariants(rest=base, workout=workout),
            variants_basis=self._resolve_basis(template.defaults.default_variants_basis),
            variants_version=self.VARIANTS_VERSION,
            start_weight_lb=None,
            start_bmi=None,
        )

    def _resolve_basis(self, basis: str) -> GoalVariantBasis:
        try:
            return GoalVariantBasis(basis)
        except ValueError:
            return GoalVariantBasis.REST
