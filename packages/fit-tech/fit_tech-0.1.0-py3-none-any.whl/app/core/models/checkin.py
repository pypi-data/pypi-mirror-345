from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.models.base import Base

class CheckIn(Base):
    """
    Модель для хранения информации о чек-инах пользователей в спортзалах.
    Позволяет отслеживать посещения залов пользователями, включая время, местоположение и заметки.
    """
    __tablename__ = "checkins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    gym_id = Column(Integer, ForeignKey("gyms.id", ondelete="SET NULL"), nullable=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    latitude = Column(Float, nullable=True)  # Широта в момент чек-ина
    longitude = Column(Float, nullable=True)  # Долгота в момент чек-ина
    location = Column(String(255), nullable=True)  # Текстовое описание местоположения
    notes = Column(Text, nullable=True)  # Заметки пользователя
    workout_id = Column(Integer, ForeignKey("workouts.id", ondelete="SET NULL"), nullable=True, index=True)  # Связанная тренировка
    duration = Column(Integer, nullable=True)  # Длительность пребывания в минутах
    is_verified = Column(Boolean, default=False, index=True)  # Подтвержден ли чек-ин (например, по геолокации)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Отношения
    user = relationship("User", back_populates="checkins")
    gym = relationship("Gym", back_populates="checkins")
    workout = relationship("Workout", back_populates="checkins")
    
    def __repr__(self):
        return f"<CheckIn(id={self.id}, user_id={self.user_id}, gym_id={self.gym_id}, timestamp={self.timestamp})>"
