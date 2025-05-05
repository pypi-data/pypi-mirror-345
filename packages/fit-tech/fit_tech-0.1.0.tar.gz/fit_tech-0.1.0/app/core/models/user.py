from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, default="user")  # user, admin, trainer
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    telegram_id = Column(String, unique=True, nullable=True)

    # Relationships
    workouts = relationship("Workout", back_populates="user")
    recipes = relationship("Recipe", back_populates="author")
    exercises = relationship("Exercise", back_populates="author")
    meal_plans = relationship("MealPlan", back_populates="user")
    reminders = relationship("Reminder", back_populates="user")
    calendar_events = relationship("CalendarEvent", back_populates="user")
    checkins = relationship("CheckIn", back_populates="user")
