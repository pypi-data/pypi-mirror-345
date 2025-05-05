from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.db.session import get_db
from app.db.repositories.user import UserRepository
from app.db.repositories.workout import WorkoutRepository
from app.db.repositories.exercise import ExerciseRepository
from app.db.repositories.recipe import RecipeRepository
from app.db.repositories.reminder import ReminderRepository
from app.db.repositories.checkin import CheckInRepository
from app.db.repositories.gym import GymRepository
from app.db.repositories.meal_plan import MealPlanRepository
from app.db.repositories.calendar_event import CalendarEventRepository

from app.core.services.user import UserService
from app.core.services.workout import WorkoutService
from app.core.services.exercise import ExerciseService
from app.core.services.recipe import RecipeService
from app.core.services.reminder import ReminderService
from app.core.services.checkin import CheckInService
from app.core.services.gym import GymService
from app.core.services.meal_plan import MealPlanService
from app.core.services.calendar_event import CalendarEventService

from app.core.security import get_current_active_user
from app.core.models.user import User

# Type hint for database session
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_active_user)]

# --- Repositories ---
def get_user_repository(db: DbSession) -> UserRepository:
    return UserRepository(db)

def get_workout_repository(db: DbSession) -> WorkoutRepository:
    return WorkoutRepository(db)

def get_exercise_repository(db: DbSession) -> ExerciseRepository:
    return ExerciseRepository(db)

def get_recipe_repository(db: DbSession) -> RecipeRepository:
    return RecipeRepository(db)

def get_reminder_repository(db: DbSession) -> ReminderRepository:
    return ReminderRepository(db)

def get_checkin_repository(db: DbSession) -> CheckInRepository:
    return CheckInRepository(db)

def get_gym_repository(db: DbSession) -> GymRepository:
    return GymRepository(db)

def get_meal_plan_repository(db: DbSession) -> MealPlanRepository:
    return MealPlanRepository(db)

def get_calendar_event_repository(db: DbSession) -> CalendarEventRepository:
    return CalendarEventRepository(db)

# --- Services ---
def get_user_service(
    repository: UserRepository = Depends(get_user_repository)
) -> UserService:
    return UserService(repository)

def get_workout_service(
    repository: WorkoutRepository = Depends(get_workout_repository)
) -> WorkoutService:
    return WorkoutService(repository)

def get_exercise_service(
    repository: ExerciseRepository = Depends(get_exercise_repository)
) -> ExerciseService:
    return ExerciseService(repository)

def get_recipe_service(
    repository: RecipeRepository = Depends(get_recipe_repository)
) -> RecipeService:
    return RecipeService(repository)

def get_reminder_service(
    repository: ReminderRepository = Depends(get_reminder_repository)
) -> ReminderService:
    return ReminderService(repository)

def get_checkin_service(
    repository: CheckInRepository = Depends(get_checkin_repository)
) -> CheckInService:
    return CheckInService(repository)

def get_gym_service(
    repository: GymRepository = Depends(get_gym_repository)
) -> GymService:
    return GymService(repository)

def get_meal_plan_service(
    repository: MealPlanRepository = Depends(get_meal_plan_repository)
) -> MealPlanService:
    return MealPlanService(repository)

def get_calendar_event_service(
    repository: CalendarEventRepository = Depends(get_calendar_event_repository)
) -> CalendarEventService:
    return CalendarEventService(repository)

