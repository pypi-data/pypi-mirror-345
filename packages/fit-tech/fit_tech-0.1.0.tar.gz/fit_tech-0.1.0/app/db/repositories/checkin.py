from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import or_

from app.core.models.checkin import CheckIn
from app.core.schemas.checkin import CheckInCreate, CheckInUpdate
from app.db.repositories.base import BaseRepository

class CheckInRepository(BaseRepository[CheckIn, CheckInCreate, CheckInUpdate]):
    def __init__(self, db: Session):
        super().__init__(CheckIn, db)

    async def get_multi_by_user(
        self, *, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100, 
        gym_id: Optional[int] = None,
        workout_id: Optional[int] = None
    ) -> List[CheckIn]:
        query = select(self.model).where(self.model.user_id == user_id)
        
        if gym_id is not None:
            query = query.where(self.model.gym_id == gym_id)
            
        if workout_id is not None:
            query = query.where(self.model.workout_id == workout_id)
            
        query = query.order_by(self.model.timestamp.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_for_user(self, *, obj_in: CheckInCreate, user_id: int) -> CheckIn:
        checkin_data = obj_in.model_dump()
        db_checkin = self.model(**checkin_data, user_id=user_id)
        self.db.add(db_checkin)
        await self.db.commit()
        await self.db.refresh(db_checkin)
        return db_checkin
