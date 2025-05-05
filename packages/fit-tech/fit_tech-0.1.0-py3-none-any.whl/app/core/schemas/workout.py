from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

from app.core.models.exercise import MuscleGroup, Difficulty
from app.core.models.workout import WorkoutType

# --- Exercise Schemas ---

class ExerciseBase(BaseModel):
    name: str
    description: Optional[str] = None
    muscle_group: MuscleGroup
    difficulty: Difficulty
    equipment: Optional[str] = None
    instructions: Optional[str] = None
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    calories_per_hour: Optional[int] = None
    is_public: Optional[bool] = True

class ExerciseCreate(ExerciseBase):
    pass

class ExerciseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    muscle_group: Optional[MuscleGroup] = None
    difficulty: Optional[Difficulty] = None
    equipment: Optional[str] = None
    instructions: Optional[str] = None
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    calories_per_hour: Optional[int] = None
    is_public: Optional[bool] = None

class ExerciseInDBBase(ExerciseBase):
    id: int
    author_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class Exercise(ExerciseInDBBase):
    pass

# --- WorkoutExercise Schemas ---

class WorkoutExerciseBase(BaseModel):
    exercise_id: int
    sets: Optional[int] = 3
    reps: Optional[int] = 10
    weight: Optional[float] = None
    rest_time: Optional[int] = None # in seconds
    order: Optional[int] = 0

class WorkoutExerciseCreate(WorkoutExerciseBase):
    pass

class WorkoutExerciseUpdate(BaseModel):
    exercise_id: Optional[int] = None
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight: Optional[float] = None
    rest_time: Optional[int] = None
    order: Optional[int] = None

class WorkoutExerciseInDBBase(WorkoutExerciseBase):
    id: int
    workout_id: int
    model_config = ConfigDict(from_attributes=True)

class WorkoutExercise(WorkoutExerciseInDBBase):
    exercise: Optional[Exercise] = None # Embed related exercise details

# --- Workout Schemas ---

class WorkoutBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: Optional[WorkoutType] = WorkoutType.OTHER
    duration: Optional[int] = None # in minutes
    calories_burned: Optional[int] = None
    scheduled_date: Optional[datetime] = None

class WorkoutCreate(WorkoutBase):
    exercises: List[WorkoutExerciseCreate] = []

class WorkoutUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[WorkoutType] = None
    duration: Optional[int] = None
    calories_burned: Optional[int] = None
    completed: Optional[bool] = None
    scheduled_date: Optional[datetime] = None
    exercises: Optional[List[WorkoutExerciseCreate]] = None # Allow updating exercises

class WorkoutInDBBase(WorkoutBase):
    id: int
    user_id: int
    completed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class Workout(WorkoutInDBBase):
    exercises: List[WorkoutExercise] = [] # Embed related workout exercises

# --- Workout Template Schema (Example) ---
class WorkoutTemplate(BaseModel):
    name: str
    description: Optional[str] = None
    type: WorkoutType
    difficulty: Difficulty
    goal: str = Field(..., description="Цель: strength, cardio, weight_loss, muscle_gain, endurance")
    duration: int = Field(..., description="Примерная продолжительность в минутах")
