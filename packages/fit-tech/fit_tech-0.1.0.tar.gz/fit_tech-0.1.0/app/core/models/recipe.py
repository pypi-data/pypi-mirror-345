from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.models.base import Base

class Recipe(Base):
    """
    Модель для хранения информации о рецептах.
    Содержит данные о названии, описании, времени приготовления, калорийности и других характеристиках рецепта.
    """
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=False)
    prep_time = Column(Integer, nullable=True)  # Время подготовки в минутах
    cook_time = Column(Integer, nullable=True)  # Время приготовления в минутах
    total_time = Column(Integer, nullable=True)  # Общее время в минутах
    servings = Column(Integer, nullable=False, default=1)
    calories = Column(Float, nullable=True)  # Калории на порцию
    protein = Column(Float, nullable=True)  # Белки на порцию (г)
    carbs = Column(Float, nullable=True)  # Углеводы на порцию (г)
    fat = Column(Float, nullable=True)  # Жиры на порцию (г)
    image_url = Column(String(255), nullable=True)
    difficulty = Column(String(50), nullable=True)  # Сложность (легкий, средний, сложный)
    cuisine = Column(String(100), nullable=True)  # Кухня (итальянская, японская и т.д.)
    meal_type = Column(String(100), nullable=True)  # Тип блюда (завтрак, обед, ужин)
    is_vegetarian = Column(Boolean, default=False)
    is_vegan = Column(Boolean, default=False)
    is_gluten_free = Column(Boolean, default=False)
    is_dairy_free = Column(Boolean, default=False)
    is_keto = Column(Boolean, default=False)
    is_paleo = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Автор рецепта
    
    # Отношения
    recipe_ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    meal_plan_recipes = relationship("MealPlanRecipe", back_populates="recipe", cascade="all, delete-orphan")
    author = relationship("User", back_populates="recipes")
    
    def __repr__(self):
        return f"<Recipe(id={self.id}, name='{self.name}', calories={self.calories})>"