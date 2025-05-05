from typing import List, Optional
from app.core.models.exercise import Exercise, MuscleGroup, Difficulty
from app.core.schemas.workout import ExerciseCreate, ExerciseUpdate
from app.db.repositories.exercise import ExerciseRepository
from app.core.services.base import BaseService

class ExerciseService(BaseService[Exercise, ExerciseCreate, ExerciseUpdate]):
    def __init__(self, repository: ExerciseRepository):
        super().__init__(repository)
        self.repository = repository
    
    async def get_multi_filtered(
        self, *, 
        skip: int = 0, 
        limit: int = 100, 
        search: Optional[str] = None, 
        muscle_group: Optional[MuscleGroup] = None, 
        difficulty: Optional[Difficulty] = None,
        is_public: Optional[bool] = True
    ) -> List[Exercise]:
        return await self.repository.get_multi_filtered(
            skip=skip, 
            limit=limit, 
            search=search, 
            muscle_group=muscle_group, 
            difficulty=difficulty,
            is_public=is_public
        )
    
    async def create_with_author(self, *, obj_in: ExerciseCreate, author_id: Optional[int] = None) -> Exercise:
        return await self.repository.create_with_author(obj_in=obj_in, author_id=author_id)
