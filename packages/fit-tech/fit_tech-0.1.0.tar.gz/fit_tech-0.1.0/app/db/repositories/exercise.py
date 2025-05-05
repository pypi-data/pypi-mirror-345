from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import or_

from app.core.models.exercise import Exercise, MuscleGroup, Difficulty
from app.core.schemas.workout import ExerciseCreate, ExerciseUpdate # Use schemas from workout.py for now
from app.db.repositories.base import BaseRepository

class ExerciseRepository(BaseRepository[Exercise, ExerciseCreate, ExerciseUpdate]):
    def __init__(self, db: Session):
        super().__init__(Exercise, db)

    async def get_multi_filtered(
        self, *, 
        skip: int = 0, 
        limit: int = 100, 
        search: Optional[str] = None, 
        muscle_group: Optional[MuscleGroup] = None, 
        difficulty: Optional[Difficulty] = None,
        is_public: Optional[bool] = True # Default to public exercises
    ) -> List[Exercise]:
        query = select(self.model)
        
        if is_public is not None:
            query = query.where(self.model.is_public == is_public)
            
        if search:
            query = query.where(
                or_(
                    self.model.name.ilike(f"%{search}%"),
                    self.model.description.ilike(f"%{search}%")
                )
            )
        if muscle_group:
            query = query.where(self.model.muscle_group == muscle_group)
        if difficulty:
            query = query.where(self.model.difficulty == difficulty)
            
        query = query.order_by(self.model.name).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_with_author(self, *, obj_in: ExerciseCreate, author_id: Optional[int] = None) -> Exercise:
        exercise_data = obj_in.model_dump()
        db_exercise = self.model(**exercise_data, author_id=author_id)
        self.db.add(db_exercise)
        await self.db.commit()
        await self.db.refresh(db_exercise)
        return db_exercise
