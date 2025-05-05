from typing import List, Optional
from app.core.models.gym import Gym, GymType
from app.core.schemas.checkin import GymCreate, GymUpdate
from app.db.repositories.gym import GymRepository
from app.core.services.base import BaseService

class GymService(BaseService[Gym, GymCreate, GymUpdate]):
    def __init__(self, repository: GymRepository):
        super().__init__(repository)
        self.repository = repository
    
    async def get_multi_filtered(
        self, *, 
        skip: int = 0, 
        limit: int = 100, 
        search: Optional[str] = None, 
        gym_type: Optional[GymType] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius: Optional[int] = None
    ) -> List[Gym]:
        return await self.repository.get_multi_filtered(
            skip=skip, 
            limit=limit, 
            search=search, 
            gym_type=gym_type,
            latitude=latitude,
            longitude=longitude,
            radius=radius
        )
