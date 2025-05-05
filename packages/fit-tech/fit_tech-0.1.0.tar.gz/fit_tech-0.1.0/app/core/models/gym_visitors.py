from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.core.models.base import Base, BaseModel

class GymVisitors(Base, BaseModel):
    """Модель для отслеживания количества посетителей в спортзале"""
    
    __tablename__ = "gym_visitors"
    
    gym_id = Column(Integer, ForeignKey("gyms.id"), nullable=False, unique=True, index=True)
    count = Column(Integer, nullable=False, default=0)
    
    # Отношения
    gym = relationship("Gym", back_populates="gym_visitors")
    
    def __repr__(self):
        return f"<GymVisitors(gym_id={self.gym_id}, count={self.count})>"
