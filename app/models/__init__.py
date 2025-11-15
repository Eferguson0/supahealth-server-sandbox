# Import all models explicitly
from .auth.user import AuthUser
from .chat.conversation import ChatConversation
from .chat.message import ChatMessage
from .enums import DataSource
from .goal.general import GoalGeneral
from .goal.macros import GoalMacros
from .goal.user_goals import UserGoal
from .goal.templates import GoalTemplate
from .metric.activity.miles import ActivityMiles
from .metric.activity.steps import ActivitySteps
from .metric.activity.workouts import ActivityWorkouts
from .metric.body.composition import BodyComposition
from .metric.body.heartrate import BodyHeartRate
from .metric.calories.active import CaloriesActive
from .metric.calories.baseline import CaloriesBaseline
from .metric.sleep.daily import SleepDaily
from .nutrition.macros import NutritionMacros
from .nutrition.foods import Food
from .nutrition.consumption_logs import ConsumptionLog
from .profile.user_profile import UserProfile

__all__ = [
    "AuthUser",
    "ChatConversation",
    "ChatMessage",
    "DataSource",
    "GoalGeneral",
    "GoalMacros",
    "UserGoal",
    "GoalTemplate",
    "BodyComposition",
    "BodyHeartRate",
    "ActivitySteps",
    "ActivityMiles",
    "ActivityWorkouts",
    "CaloriesBaseline",
    "CaloriesActive",
    "SleepDaily",
    "NutritionMacros",
    "Food",
    "ConsumptionLog",
    "UserProfile",
]
