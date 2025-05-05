from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

from app.core.models.gym import GymType

# --- Gym Schemas ---

class GymBase(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float
    description: Optional[str] = None
    opening_hours: Optional[str] = None
    gym_type: Optional[GymType] = GymType.FITNESS
    phone: Optional[str] = None
    website: Optional[str] = None
    image_url: Optional[str] = None
    is_verified: Optional[bool] = False

class GymCreate(GymBase):
    pass

class GymUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    description: Optional[str] = None
    opening_hours: Optional[str] = None
    gym_type: Optional[GymType] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    image_url: Optional[str] = None
    is_verified: Optional[bool] = None

class GymInDBBase(GymBase):
    id: int
    # location: Optional[str] = None # GeoAlchemy field, handle separately if needed for response
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class Gym(GymInDBBase):
    pass

# --- CheckIn Schemas ---

class CheckInBase(BaseModel):
    gym_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notes: Optional[str] = None
    workout_id: Optional[int] = None
    duration: Optional[int] = None
    is_verified: Optional[bool] = False

class CheckInCreate(CheckInBase):
    pass

class CheckInUpdate(BaseModel):
    gym_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notes: Optional[str] = None
    workout_id: Optional[int] = None
    duration: Optional[int] = None
    is_verified: Optional[bool] = None

class CheckInInDBBase(CheckInBase):
    id: int
    user_id: int
    timestamp: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class CheckIn(CheckInInDBBase):
    gym: Optional[Gym] = None
    # workout: Optional[Workout] = None # Add if Workout schema is defined and needed

# --- GymVisitors Schemas ---

class GymVisitorsBase(BaseModel):
    gym_id: int
    count: int = 0

class GymVisitorsCreate(GymVisitorsBase):
    pass

class GymVisitorsUpdate(BaseModel):
    count: Optional[int] = None

class GymVisitorsInDBBase(GymVisitorsBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class GymVisitors(GymVisitorsInDBBase):
    pass

class GymVisitorsResponse(BaseModel):
    gym_id: int
    count: int
    updated_at: Optional[datetime] = None
