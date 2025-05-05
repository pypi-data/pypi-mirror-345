from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Table, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
import enum

from app.core.models.base import Base

class GymType(str, enum.Enum):
    FITNESS = "fitness"
    CROSSFIT = "crossfit"
    YOGA = "yoga"
    SWIMMING = "swimming"
    MARTIAL_ARTS = "martial_arts"
    OTHER = "other"

class Gym(Base):
    __tablename__ = "gyms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    address = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    # location = Column(Geography(geometry_type='POINT', srid=4326), nullable=True)
    description = Column(String(500), nullable=True)
    opening_hours = Column(String(255), nullable=True)
    gym_type = Column(Enum(GymType), default=GymType.FITNESS, nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    website = Column(String(255), nullable=True)
    image_url = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    checkins = relationship("CheckIn", back_populates="gym", cascade="all, delete-orphan")
    gym_visitors = relationship("GymVisitors", back_populates="gym", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Gym(id={self.id}, name='{self.name}', address='{self.address}')>"
