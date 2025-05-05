from typing import List, Optional, Dict
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.future import select

from app.core.models.workout import Workout
from app.core.models.workout_exercise import WorkoutExercise
from app.core.schemas.workout import WorkoutCreate, WorkoutUpdate
from app.db.repositories.base import BaseRepository

class WorkoutRepository(BaseRepository[Workout, WorkoutCreate, WorkoutUpdate]):
    def __init__(self, db: Session):
        super().__init__(Workout, db)
    
    async def get_with_exercises(self, id: int) -> Optional[Workout]:
        query = select(Workout).options(
            joinedload(Workout.workout_exercises).joinedload(WorkoutExercise.exercise)
        ).where(Workout.id == id)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_multi_by_user(
        self, *, user_id: int, skip: int = 0, limit: int = 100, 
        type: Optional[str] = None, completed: Optional[bool] = None
    ) -> List[Workout]:
        query = select(Workout).where(Workout.user_id == user_id)
        
        if type:
            query = query.where(Workout.type == type)
        if completed is not None:
            query = query.where(Workout.completed == completed)
        
        query = query.order_by(Workout.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
