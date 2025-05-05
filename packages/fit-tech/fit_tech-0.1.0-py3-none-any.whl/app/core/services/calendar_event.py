from typing import List, Optional
from datetime import datetime
from app.core.models.calendar_event import CalendarEvent
from app.core.schemas.calendar_event import CalendarEventCreate, CalendarEventUpdate
from app.db.repositories.calendar_event import CalendarEventRepository
from app.core.services.base import BaseService

class CalendarEventService(BaseService[CalendarEvent, CalendarEventCreate, CalendarEventUpdate]):
    def __init__(self, repository: CalendarEventRepository):
        super().__init__(repository)
        self.repository = repository
    
    async def get_multi_by_user(
        self, *, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_type: Optional[str] = None
    ) -> List[CalendarEvent]:
        return await self.repository.get_multi_by_user(
            user_id=user_id,
            skip=skip,
            limit=limit,
            start_date=start_date,
            end_date=end_date,
            event_type=event_type
        )
    
    async def create_for_user(self, *, obj_in: CalendarEventCreate, user_id: int) -> CalendarEvent:
        return await self.repository.create_for_user(obj_in=obj_in, user_id=user_id)
