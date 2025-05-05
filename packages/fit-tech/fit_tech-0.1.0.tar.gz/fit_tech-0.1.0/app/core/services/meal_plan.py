from typing import List, Optional
from app.core.models.meal_plan import MealPlan
from app.core.schemas.meal_plan import MealPlanCreate, MealPlanUpdate
from app.db.repositories.meal_plan import MealPlanRepository
from app.core.services.base import BaseService

class MealPlanService(BaseService[MealPlan, MealPlanCreate, MealPlanUpdate]):
    def __init__(self, repository: MealPlanRepository):
        super().__init__(repository)
        self.repository = repository
    
    async def get_with_recipes(self, id: int) -> Optional[MealPlan]:
        return await self.repository.get_with_recipes(id=id)
    
    async def get_multi_by_user(
        self, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[MealPlan]:
        return await self.repository.get_multi_by_user(
            user_id=user_id, skip=skip, limit=limit
        )
    
    async def create_with_recipes(self, *, obj_in: MealPlanCreate, user_id: int) -> MealPlan:
        return await self.repository.create_with_recipes(obj_in=obj_in, user_id=user_id)
    
    async def update_with_recipes(self, *, id: int, obj_in: MealPlanUpdate) -> MealPlan:
        db_obj = await self.repository.get(id=id)
        if not db_obj:
            return None
        return await self.repository.update_with_recipes(db_obj=db_obj, obj_in=obj_in)
