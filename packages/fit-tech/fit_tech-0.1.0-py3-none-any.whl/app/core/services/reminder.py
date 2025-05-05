from typing import List, Optional
from app.core.models.reminder import Reminder, RepeatType
from app.core.schemas.reminder import ReminderCreate, ReminderUpdate
from app.db.repositories.reminder import ReminderRepository
from app.core.services.base import BaseService

class ReminderService(BaseService[Reminder, ReminderCreate, ReminderUpdate]):
    def __init__(self, repository: ReminderRepository):
        super().__init__(repository)
        self.repository = repository
    
    async def get_multi_by_user(
        self, *, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100, 
        is_active: Optional[bool] = None,
        repeat_type: Optional[RepeatType] = None
    ) -> List[Reminder]:
        return await self.repository.get_multi_by_user(
            user_id=user_id,
            skip=skip,
            limit=limit,
            is_active=is_active,
            repeat_type=repeat_type
        )
    
    async def create_for_user(self, *, obj_in: ReminderCreate, user_id: int) -> Reminder:
        return await self.repository.create_for_user(obj_in=obj_in, user_id=user_id)
