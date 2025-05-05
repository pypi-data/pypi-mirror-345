from typing import List, Optional
from app.core.models.recipe import Recipe
from app.core.schemas.recipe import RecipeCreate, RecipeUpdate, RecipeIngredientCreate
from app.db.repositories.recipe import RecipeRepository
from app.core.services.base import BaseService

class RecipeService(BaseService[Recipe, RecipeCreate, RecipeUpdate]):
    def __init__(self, repository: RecipeRepository):
        super().__init__(repository)
        self.repository = repository
    
    async def get_with_ingredients(self, id: int) -> Optional[Recipe]:
        return await self.repository.get_with_ingredients(id=id)
    
    async def get_multi_by_user(
        self, *, user_id: int, skip: int = 0, limit: int = 100, 
        search: Optional[str] = None, cuisine: Optional[str] = None, meal_type: Optional[str] = None,
        max_calories: Optional[int] = None, min_protein: Optional[float] = None
    ) -> List[Recipe]:
        return await self.repository.get_multi_by_user(
            user_id=user_id, skip=skip, limit=limit, 
            search=search, cuisine=cuisine, meal_type=meal_type,
            max_calories=max_calories, min_protein=min_protein
        )
    
    async def create_with_ingredients(self, *, obj_in: RecipeCreate, user_id: int) -> Recipe:
        return await self.repository.create_with_ingredients(obj_in=obj_in, user_id=user_id)
    
    async def update_with_ingredients(self, *, id: int, obj_in: RecipeUpdate) -> Recipe:
        db_obj = await self.repository.get(id=id)
        if not db_obj:
            return None
        return await self.repository.update_with_ingredients(db_obj=db_obj, obj_in=obj_in)
