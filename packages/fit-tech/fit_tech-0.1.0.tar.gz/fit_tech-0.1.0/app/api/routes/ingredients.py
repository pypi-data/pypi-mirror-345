from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.models.ingredient import Ingredient
from app.core.models.user import User
from app.core.schemas.recipe import (
    Ingredient as IngredientSchema,
    IngredientCreate,
    IngredientUpdate,
)
from app.core.security import get_current_active_user, get_current_superuser
from app.db.session import get_db

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


@router.get("/", response_model=List[IngredientSchema])
def get_ingredients(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Получить список ингредиентов с возможностью поиска
    """
    query = db.query(Ingredient)

    # Поиск по названию
    if search:
        query = query.filter(Ingredient.name.ilike(f"%{search}%"))

    ingredients = query.order_by(Ingredient.name).offset(skip).limit(limit).all()
    return ingredients


@router.post("/", response_model=IngredientSchema, status_code=status.HTTP_201_CREATED)
def create_ingredient(
    ingredient_in: IngredientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Создать новый ингредиент (только для администраторов)
    """
    existing_ingredient = (
        db.query(Ingredient).filter(Ingredient.name == ingredient_in.name).first()
    )
    if existing_ingredient:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ингредиент с названием '{ingredient_in.name}' уже существует",
        )

    ingredient = Ingredient(
        name=ingredient_in.name,
        calories=ingredient_in.calories,
        protein=ingredient_in.protein,
        carbs=ingredient_in.carbs,
        fat=ingredient_in.fat,
        unit=ingredient_in.unit,
    )
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)
    return ingredient


@router.get("/{ingredient_id}", response_model=IngredientSchema)
def get_ingredient(
    ingredient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Получить детали ингредиента по ID
    """
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()

    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ингредиент не найден"
        )

    return ingredient


@router.put("/{ingredient_id}", response_model=IngredientSchema)
def update_ingredient(
    ingredient_id: int,
    ingredient_in: IngredientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Обновить ингредиент (только для администраторов)
    """
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()

    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ингредиент не найден"
        )

    if ingredient_in.name and ingredient_in.name != ingredient.name:
        existing_ingredient = (
            db.query(Ingredient).filter(Ingredient.name == ingredient_in.name).first()
        )
        if existing_ingredient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ингредиент с названием '{ingredient_in.name}' уже существует",
            )

    update_data = ingredient_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ingredient, field, value)

    db.commit()
    db.refresh(ingredient)
    return ingredient


@router.delete("/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingredient(
    ingredient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Удалить ингредиент (только для администраторов)
    """
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()

    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ингредиент не найден"
        )

    if ingredient.recipes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Невозможно удалить ингредиент, так как он используется в рецептах",
        )

    db.delete(ingredient)
    db.commit()
    return None
