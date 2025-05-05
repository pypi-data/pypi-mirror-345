from typing import List, Optional
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.future import select
from sqlalchemy import delete

from app.core.models.meal_plan import MealPlan
from app.core.models.meal_plan_recipe import MealPlanRecipe
from app.core.schemas.meal_plan import MealPlanCreate, MealPlanUpdate
from app.db.repositories.base import BaseRepository

class MealPlanRepository(BaseRepository[MealPlan, MealPlanCreate, MealPlanUpdate]):
    def __init__(self, db: Session):
        super().__init__(MealPlan, db)

    async def get_with_recipes(self, id: int) -> Optional[MealPlan]:
        query = select(self.model).options(selectinload(self.model.meal_plan_recipes).selectinload(MealPlanRecipe.recipe)).where(self.model.id == id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_multi_by_user(
        self, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[MealPlan]:
        query = select(self.model).where(self.model.user_id == user_id)
        query = query.order_by(self.model.name).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_with_recipes(self, *, obj_in: MealPlanCreate, user_id: int) -> MealPlan:
        meal_plan_data = obj_in.model_dump(exclude={"recipes"})
        db_meal_plan = self.model(**meal_plan_data, user_id=user_id)
        self.db.add(db_meal_plan)
        await self.db.flush()

        for recipe_in in obj_in.recipes:
            db_recipe = MealPlanRecipe(
                meal_plan_id=db_meal_plan.id,
                **recipe_in.model_dump()
            )
            self.db.add(db_recipe)
            
        await self.db.commit()
        await self.db.refresh(db_meal_plan)
        return await self.get_with_recipes(id=db_meal_plan.id)

    async def update_with_recipes(self, *, db_obj: MealPlan, obj_in: MealPlanUpdate) -> MealPlan:
        update_data = obj_in.model_dump(exclude_unset=True, exclude={"recipes"})
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        if obj_in.recipes is not None:
            await self.db.execute(delete(MealPlanRecipe).where(MealPlanRecipe.meal_plan_id == db_obj.id))

            for recipe_in in obj_in.recipes:
                db_recipe = MealPlanRecipe(
                    meal_plan_id=db_obj.id,
                    **recipe_in.model_dump()
                )
                self.db.add(db_recipe)

        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return await self.get_with_recipes(id=db_obj.id)
