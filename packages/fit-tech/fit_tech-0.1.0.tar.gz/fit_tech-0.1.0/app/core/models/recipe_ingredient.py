from sqlalchemy import Column, String, Integer, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship

from app.core.models.base import Base, BaseModel
import enum


class UnitType(str, enum.Enum):
    GRAM = "g"
    MILLILITER = "ml"
    PIECE = "pc"
    TABLESPOON = "tbsp"
    TEASPOON = "tsp"
    CUP = "cup"


class RecipeIngredient(Base, BaseModel):
    """Модель связи между рецептом и ингредиентом"""

    __tablename__ = "recipe_ingredients"

    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False, index=True)
    ingredient_id = Column(
        Integer, ForeignKey("ingredients.id"), nullable=False, index=True
    )
    amount = Column(Float, nullable=False)
    unit = Column(Enum(UnitType), nullable=False, default=UnitType.GRAM)

    # Отношения
    recipe = relationship("Recipe", back_populates="recipe_ingredients")
    ingredient = relationship("Ingredient", back_populates="recipe_ingredients")

    def __repr__(self):
        return f"<RecipeIngredient(recipe_id={self.recipe_id}, ingredient_id={self.ingredient_id}, amount={self.amount}, unit='{self.unit}')>"
