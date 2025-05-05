from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import or_

from app.core.models.reminder import Reminder, RepeatType
from app.core.schemas.reminder import ReminderCreate, ReminderUpdate
from app.db.repositories.base import BaseRepository

class ReminderRepository(BaseRepository[Reminder, ReminderCreate, ReminderUpdate]):
    def __init__(self, db: Session):
        super().__init__(Reminder, db)

    async def get_multi_by_user(
        self, *, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100, 
        is_active: Optional[bool] = None,
        repeat_type: Optional[RepeatType] = None
    ) -> List[Reminder]:
        query = select(self.model).where(self.model.user_id == user_id)
        
        if is_active is not None:
            query = query.where(self.model.is_active == is_active)
            
        if repeat_type:
            query = query.where(self.model.repeat_type == repeat_type)
            
        query = query.order_by(self.model.reminder_time).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_for_user(self, *, obj_in: ReminderCreate, user_id: int) -> Reminder:
        reminder_data = obj_in.model_dump()
        db_reminder = self.model(**reminder_data, user_id=user_id)
        self.db.add(db_reminder)
        await self.db.commit()
        await self.db.refresh(db_reminder)
        return db_reminder
