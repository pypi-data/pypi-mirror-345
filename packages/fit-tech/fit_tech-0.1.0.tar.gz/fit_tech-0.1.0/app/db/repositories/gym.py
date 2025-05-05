from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import func, or_
from geoalchemy2.functions import ST_DWithin

from app.core.models.gym import Gym, GymType
from app.core.schemas.checkin import GymCreate, GymUpdate
from app.db.repositories.base import BaseRepository

class GymRepository(BaseRepository[Gym, GymCreate, GymUpdate]):
    def __init__(self, db: Session):
        super().__init__(Gym, db)

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
        query = select(self.model)
        
        if search:
            query = query.where(
                or_(
                    self.model.name.ilike(f"%{search}%"),
                    self.model.address.ilike(f"%{search}%"),
                    self.model.description.ilike(f"%{search}%")
                )
            )
        if gym_type:
            query = query.where(self.model.gym_type == gym_type)
            
        if latitude is not None and longitude is not None and radius is not None:
            point = f'POINT({longitude} {latitude})'
            query = query.where(ST_DWithin(self.model.location, point, radius))
            
        query = query.order_by(self.model.name).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
