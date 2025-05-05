from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.core.models.base import Base, BaseModel

class WorkoutExercise(Base, BaseModel):
    """Модель связи между тренировкой и упражнением"""
    
    __tablename__ = "workout_exercises"
    
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False, index=True)
    sets = Column(Integer, nullable=False, default=3)
    reps = Column(Integer, nullable=False, default=10)
    weight = Column(Float, nullable=True)
    rest_time = Column(Integer, nullable=True)  # в секундах
    order = Column(Integer, nullable=False, default=0)
    
    # Отношения
    workout = relationship("Workout", back_populates="workout_exercises")
    exercise = relationship("Exercise", back_populates="workout_exercises")
    
    def __repr__(self):
        return f"<WorkoutExercise(workout_id={self.workout_id}, exercise_id={self.exercise_id}, sets={self.sets}, reps={self.reps})>"
