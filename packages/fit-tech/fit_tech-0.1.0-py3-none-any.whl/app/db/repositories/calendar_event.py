from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from datetime import datetime

from app.core.models.calendar_event import CalendarEvent
from app.core.schemas.calendar_event import CalendarEventCreate, CalendarEventUpdate
from app.db.repositories.base import BaseRepository

class CalendarEventRepository(BaseRepository[CalendarEvent, CalendarEventCreate, CalendarEventUpdate]):
    def __init__(self, db: Session):
        super().__init__(CalendarEvent, db)

    async def get_multi_by_user(
        self, *, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_type: Optional[str] = None
    ) -> List[CalendarEvent]:
        query = select(self.model).where(self.model.user_id == user_id)
        
        if start_date:
            query = query.where(self.model.start_time >= start_date)
            
        if end_date:
            query = query.where(self.model.start_time <= end_date)
            
        if event_type:
            query = query.where(self.model.event_type == event_type)
            
        query = query.order_by(self.model.start_time).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_for_user(self, *, obj_in: CalendarEventCreate, user_id: int) -> CalendarEvent:
        event_data = obj_in.model_dump()
        db_event = self.model(**event_data, user_id=user_id)
        self.db.add(db_event)
        await self.db.commit()
        await self.db.refresh(db_event)
        return db_event
