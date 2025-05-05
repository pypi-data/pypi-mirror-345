from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas.recipe import Recipe, RecipeCreate, RecipeUpdate, RecipeIngredientCreate
from app.core.services.recipe import RecipeService
from app.api.dependencies import get_recipe_service, CurrentUser, DbSession

router = APIRouter()

@router.post("/", response_model=Recipe, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    recipe_in: RecipeCreate,
    current_user: CurrentUser,
    recipe_service: RecipeService = Depends(get_recipe_service)
):
    """
    Создать новый рецепт для текущего пользователя
    """
    recipe = await recipe_service.create_with_ingredients(obj_in=recipe_in, user_id=current_user.id)
    return recipe

@router.get("/", response_model=List[Recipe])
async def get_recipes(
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    cuisine: Optional[str] = None,
    meal_type: Optional[str] = None,
    max_calories: Optional[int] = Query(None, description="Maximum calories per serving"),
    min_protein: Optional[float] = Query(None, description="Minimum protein per serving (grams)"),
    recipe_service: RecipeService = Depends(get_recipe_service)
):
    """
    Получить список рецептов текущего пользователя с возможностью фильтрации
    """
    recipes = await recipe_service.get_multi_by_user(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        search=search,
        cuisine=cuisine,
        meal_type=meal_type,
        max_calories=max_calories,
        min_protein=min_protein
    )
    return recipes

@router.get("/{recipe_id}", response_model=Recipe)
async def get_recipe(
    recipe_id: int,
    current_user: CurrentUser,
    recipe_service: RecipeService = Depends(get_recipe_service)
):
    """
    Получить детали конкретного рецепта
    """
    recipe = await recipe_service.get_with_ingredients(id=recipe_id)
    if not recipe:
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    if recipe.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this recipe"
        )
    return recipe

@router.put("/{recipe_id}", response_model=Recipe)
async def update_recipe(
    recipe_id: int,
    recipe_in: RecipeUpdate,
    current_user: CurrentUser,
    recipe_service: RecipeService = Depends(get_recipe_service)
):
    """
    Обновить рецепт
    """
    recipe = await recipe_service.get(id=recipe_id)
    if not recipe or recipe.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found or not owned by user"
        )
    
    recipe = await recipe_service.update_with_ingredients(id=recipe_id, obj_in=recipe_in)
    return recipe

@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: int,
    current_user: CurrentUser,
    recipe_service: RecipeService = Depends(get_recipe_service)
):
    """
    Удалить рецепт
    """
    recipe = await recipe_service.get(id=recipe_id)
    if not recipe or recipe.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found or not owned by user"
        )
    
    await recipe_service.delete(id=recipe_id)
    return None

