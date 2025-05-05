from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

from app.core.models.recipe_ingredient import UnitType

# --- Ingredient Schemas ---

class IngredientBase(BaseModel):
    name: str
    description: Optional[str] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    fiber: Optional[float] = None
    sugar: Optional[float] = None
    unit: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    is_vegetarian: Optional[bool] = True
    is_vegan: Optional[bool] = False
    is_gluten_free: Optional[bool] = True
    is_dairy_free: Optional[bool] = True

class IngredientCreate(IngredientBase):
    pass

class IngredientUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    fiber: Optional[float] = None
    sugar: Optional[float] = None
    unit: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    is_vegetarian: Optional[bool] = None
    is_vegan: Optional[bool] = None
    is_gluten_free: Optional[bool] = None
    is_dairy_free: Optional[bool] = None

class IngredientInDBBase(IngredientBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class Ingredient(IngredientInDBBase):
    pass

# --- RecipeIngredient Schemas ---

class RecipeIngredientBase(BaseModel):
    ingredient_id: int
    amount: float
    unit: UnitType

class RecipeIngredientCreate(RecipeIngredientBase):
    pass

class RecipeIngredientUpdate(BaseModel):
    ingredient_id: Optional[int] = None
    amount: Optional[float] = None
    unit: Optional[UnitType] = None

class RecipeIngredientInDBBase(RecipeIngredientBase):
    id: int
    recipe_id: int
    model_config = ConfigDict(from_attributes=True)

class RecipeIngredient(RecipeIngredientInDBBase):
    ingredient: Optional[Ingredient] = None # Embed related ingredient details

# --- Recipe Schemas ---

class RecipeBase(BaseModel):
    name: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    prep_time: Optional[int] = None
    cook_time: Optional[int] = None
    total_time: Optional[int] = None
    servings: Optional[int] = 1
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    image_url: Optional[str] = None
    difficulty: Optional[str] = None
    cuisine: Optional[str] = None
    meal_type: Optional[str] = None
    is_vegetarian: Optional[bool] = False
    is_vegan: Optional[bool] = False
    is_gluten_free: Optional[bool] = False
    is_dairy_free: Optional[bool] = False
    is_keto: Optional[bool] = False
    is_paleo: Optional[bool] = False

class RecipeCreate(RecipeBase):
    ingredients: List[RecipeIngredientCreate] = []

class RecipeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    prep_time: Optional[int] = None
    cook_time: Optional[int] = None
    total_time: Optional[int] = None
    servings: Optional[int] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    image_url: Optional[str] = None
    difficulty: Optional[str] = None
    cuisine: Optional[str] = None
    meal_type: Optional[str] = None
    is_vegetarian: Optional[bool] = None
    is_vegan: Optional[bool] = None
    is_gluten_free: Optional[bool] = None
    is_dairy_free: Optional[bool] = None
    is_keto: Optional[bool] = None
    is_paleo: Optional[bool] = None
    ingredients: Optional[List[RecipeIngredientCreate]] = None # Allow updating ingredients

class RecipeInDBBase(RecipeBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class Recipe(RecipeInDBBase):
    ingredients: List[RecipeIngredient] = [] # Embed related recipe ingredients

