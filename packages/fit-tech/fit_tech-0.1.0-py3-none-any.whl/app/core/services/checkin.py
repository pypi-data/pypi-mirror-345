from typing import List, Optional
from app.core.models.checkin import CheckIn
from app.core.schemas.checkin import CheckInCreate, CheckInUpdate
from app.db.repositories.checkin import CheckInRepository
from app.core.services.base import BaseService

class CheckInService(BaseService[CheckIn, CheckInCreate, CheckInUpdate]):
    def __init__(self, repository: CheckInRepository):
        super().__init__(repository)
        self.repository = repository
    
    async def get_multi_by_user(
        self, *, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100, 
        gym_id: Optional[int] = None,
        workout_id: Optional[int] = None
    ) -> List[CheckIn]:
        return await self.repository.get_multi_by_user(
            user_id=user_id,
            skip=skip,
            limit=limit,
            gym_id=gym_id,
            workout_id=workout_id
        )
    
    async def create_for_user(self, *, obj_in: CheckInCreate, user_id: int) -> CheckIn:
        return await self.repository.create_for_user(obj_in=obj_in, user_id=user_id)
