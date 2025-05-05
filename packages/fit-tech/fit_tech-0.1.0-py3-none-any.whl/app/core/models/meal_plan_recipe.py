from sqlalchemy import Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.core.models.base import Base, BaseModel
import enum

class MealType(str, enum.Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"

class MealPlanRecipe(Base, BaseModel):
    """Модель связи между планом питания и рецептом"""
    
    __tablename__ = "meal_plan_recipes"
    
    meal_plan_id = Column(Integer, ForeignKey("meal_plans.id"), nullable=False, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False, index=True)
    meal_type = Column(Enum(MealType), nullable=False, index=True)
    
    # Отношения
    meal_plan = relationship("MealPlan", back_populates="meal_plan_recipes")
    recipe = relationship("Recipe", back_populates="meal_plan_recipes")
    
    def __repr__(self):
        return f"<MealPlanRecipe(meal_plan_id={self.meal_plan_id}, recipe_id={self.recipe_id}, meal_type='{self.meal_type}')>"
