from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.models.base import Base

class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    duration = Column(Integer, nullable=True)  # длительность в днях
    total_calories = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="meal_plans")
    meal_plan_recipes = relationship("MealPlanRecipe", back_populates="meal_plan", cascade="all, delete-orphan")
    recipes = relationship("Recipe", secondary="meal_plan_recipes", viewonly=True)
    
    def __repr__(self):
        return f"<MealPlan(id={self.id}, name='{self.name}')>"