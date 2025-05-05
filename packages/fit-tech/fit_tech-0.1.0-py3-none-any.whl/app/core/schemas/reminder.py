from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
import enum

from app.core.models.reminder import RepeatType

# --- Reminder Schemas ---

class ReminderBase(BaseModel):
    title: str
    description: Optional[str] = None
    reminder_time: datetime
    repeat_type: RepeatType = RepeatType.NONE
    rrule: Optional[str] = None
    is_active: bool = True

class ReminderCreate(ReminderBase):
    pass

class ReminderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    reminder_time: Optional[datetime] = None
    repeat_type: Optional[RepeatType] = None
    rrule: Optional[str] = None
    is_active: Optional[bool] = None

class ReminderInDBBase(ReminderBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class Reminder(ReminderInDBBase):
    pass
