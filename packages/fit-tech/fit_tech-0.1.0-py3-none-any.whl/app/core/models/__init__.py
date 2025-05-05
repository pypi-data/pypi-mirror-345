from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime, Enum, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

# Импортируем все модели в один файл для удобства импорта
from app.core.models.base import Base, BaseModel
from app.core.models.user import User
from app.core.models.exercise import Exercise, MuscleGroup, Difficulty
from app.core.models.workout import Workout
from app.core.models.workout_exercise import WorkoutExercise
from app.core.models.recipe import Recipe
from app.core.models.ingredient import Ingredient
from app.core.models.recipe_ingredient import RecipeIngredient, UnitType
from app.core.models.meal_plan import MealPlan
from app.core.models.meal_plan_recipe import MealPlanRecipe, MealType
from app.core.models.reminder import Reminder, RepeatType
from app.core.models.calendar_event import CalendarEvent
from app.core.models.gym import Gym
from app.core.models.checkin import CheckIn
from app.core.models.gym_visitors import GymVisitors

# Экспортируем все модели
__all__ = [
    'Base', 'BaseModel',
    'User',
    'Exercise', 'MuscleGroup', 'Difficulty',
    'Workout',
    'WorkoutExercise',
    'Recipe',
    'Ingredient',
    'RecipeIngredient', 'UnitType',
    'MealPlan',
    'MealPlanRecipe', 'MealType',
    'Reminder', 'RepeatType',
    'CalendarEvent',
    'Gym',
    'CheckIn',
    'GymVisitors'
]
