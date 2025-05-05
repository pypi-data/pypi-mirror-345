from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.models.base import Base

class CalendarEvent(Base):
    """
    Модель для хранения информации о событиях календаря.
    Связывает пользователя с тренировками, напоминаниями и другими событиями.
    """
    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    all_day = Column(Boolean, default=False)
    location = Column(String(255), nullable=True)
    event_type = Column(String(50), nullable=False, index=True)  # workout, reminder, meal, etc.
    event_id = Column(Integer, nullable=True)  # ID связанного события (workout_id, reminder_id, etc.)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="calendar_events")
    
    def __repr__(self):
        return f"<CalendarEvent(id={self.id}, title='{self.title}', start_time={self.start_time})>"
