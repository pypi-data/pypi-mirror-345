from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import update, delete, func # Added func
from sqlalchemy.orm import selectinload # Corrected import

from app.core.models.recipe import Recipe
from app.core.models.recipe_ingredient import RecipeIngredient
from app.core.schemas.recipe import RecipeCreate, RecipeUpdate, RecipeIngredientCreate
from app.db.repositories.base import BaseRepository


class RecipeRepository(BaseRepository[Recipe, RecipeCreate, RecipeUpdate]):
    def __init__(self, db: Session):
        super().__init__(Recipe, db)

    async def get_with_ingredients(self, id: int) -> Optional[Recipe]:
        query = (
            select(self.model)
            .options(
                selectinload(self.model.recipe_ingredients).selectinload(
                    RecipeIngredient.ingredient
                )
            )
            .where(self.model.id == id)
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_multi_by_user(
        self,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        cuisine: Optional[str] = None,
        meal_type: Optional[str] = None,
        max_calories: Optional[int] = None,
        min_protein: Optional[float] = None
    ) -> List[Recipe]:
        query = select(self.model).where(self.model.user_id == user_id)
        if search:
            query = query.where(
                func.lower(self.model.name).contains(func.lower(search)) |
                func.lower(self.model.description).contains(func.lower(search))
            )
        if cuisine:
            query = query.where(func.lower(self.model.cuisine) == func.lower(cuisine))
        if meal_type:
            query = query.where(func.lower(self.model.meal_type) == func.lower(meal_type))

        if max_calories is not None:
            query = query.where(self.model.calories <= max_calories)
        if min_protein is not None:
            query = query.where(self.model.protein >= min_protein)

        query = query.order_by(self.model.name).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_with_ingredients(
        self, *, obj_in: RecipeCreate, user_id: int
    ) -> Recipe:
        recipe_data = obj_in.model_dump(exclude={"ingredients"})
        db_recipe = self.model(**recipe_data, user_id=user_id)
        self.db.add(db_recipe)
        await self.db.flush()

        if obj_in.ingredients:
            for ingredient_in in obj_in.ingredients:
                db_ingredient = RecipeIngredient(
                    recipe_id=db_recipe.id, **ingredient_in.model_dump()
                )
                self.db.add(db_ingredient)

        await self.db.commit()
        await self.db.refresh(db_recipe)
        return await self.get_with_ingredients(id=db_recipe.id)

    async def update_with_ingredients(
        self, *, db_obj: Recipe, obj_in: RecipeUpdate
    ) -> Recipe:
        update_data = obj_in.model_dump(exclude_unset=True, exclude={"ingredients"})
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        if obj_in.ingredients is not None:
            await self.db.execute(
                delete(RecipeIngredient).where(RecipeIngredient.recipe_id == db_obj.id)
            )

            for ingredient_in in obj_in.ingredients:
                db_ingredient = RecipeIngredient(
                    recipe_id=db_obj.id, **ingredient_in.model_dump()
                )
                self.db.add(db_ingredient)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return await self.get_with_ingredients(id=db_obj.id)

