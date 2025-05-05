from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

from app.core.models.meal_plan_recipe import MealType
from app.core.schemas.recipe import Recipe, RecipeCreate, RecipeUpdate, RecipeIngredient, RecipeIngredientCreate

# --- MealPlanRecipe Schemas ---

class MealPlanRecipeBase(BaseModel):
    recipe_id: int
    meal_type: MealType
    day: Optional[int] = None # Optional day number within the plan

class MealPlanRecipeCreate(MealPlanRecipeBase):
    pass

class MealPlanRecipeUpdate(BaseModel):
    recipe_id: Optional[int] = None
    meal_type: Optional[MealType] = None
    day: Optional[int] = None

class MealPlanRecipeInDBBase(MealPlanRecipeBase):
    id: int
    meal_plan_id: int
    model_config = ConfigDict(from_attributes=True)

class MealPlanRecipe(MealPlanRecipeInDBBase):
    recipe: Optional[Recipe] = None # Embed related recipe details

# --- MealPlan Schemas ---

class MealPlanBase(BaseModel):
    name: str
    description: Optional[str] = None
    duration: Optional[int] = None # Duration in days
    total_calories: Optional[int] = None

class MealPlanCreate(MealPlanBase):
    recipes: List[MealPlanRecipeCreate] = []

class MealPlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = None
    total_calories: Optional[int] = None
    recipes: Optional[List[MealPlanRecipeCreate]] = None # Allow updating recipes

class MealPlanInDBBase(MealPlanBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class MealPlan(MealPlanInDBBase):
    recipes: List[MealPlanRecipe] = [] # Embed related meal plan recipes
