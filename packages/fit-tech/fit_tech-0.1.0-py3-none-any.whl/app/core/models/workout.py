from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime, Boolean, Index, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.models.base import Base

class WorkoutType(str, enum.Enum):
    STRENGTH = "strength"
    CARDIO = "cardio"
    FLEXIBILITY = "flexibility"
    HIIT = "hiit"
    YOGA = "yoga"
    PILATES = "pilates"
    CROSSFIT = "crossfit"
    OTHER = "other"

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    type = Column(Enum(WorkoutType), index=True, nullable=False, default=WorkoutType.OTHER)
    duration = Column(Integer, nullable=True)  # in minutes
    calories_burned = Column(Integer, nullable=True)
    completed = Column(Boolean, default=False, index=True)
    scheduled_date = Column(DateTime(timezone=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="workouts")
    workout_exercises = relationship("WorkoutExercise", back_populates="workout", cascade="all, delete-orphan")
    checkins = relationship("CheckIn", back_populates="workout")

    # Составной индекс для часто используемых фильтров
    __table_args__ = (
        Index('idx_workout_user_completed', user_id, completed),
        Index('idx_workout_user_type', user_id, type),
        Index('idx_workout_scheduled_date', scheduled_date),
    )
    
    def __repr__(self):
        return f"<Workout(id={self.id}, name='{self.name}', type={self.type})>"
