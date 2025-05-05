from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

# --- CalendarEvent Schemas ---

class CalendarEventBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    all_day: bool = False
    location: Optional[str] = None
    event_type: str  # workout, reminder, meal, etc.
    event_id: Optional[int] = None  # ID of related event (workout_id, reminder_id, etc.)

class CalendarEventCreate(CalendarEventBase):
    pass

class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    all_day: Optional[bool] = None
    location: Optional[str] = None
    event_type: Optional[str] = None
    event_id: Optional[int] = None

class CalendarEventInDBBase(CalendarEventBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class CalendarEvent(CalendarEventInDBBase):
    pass
