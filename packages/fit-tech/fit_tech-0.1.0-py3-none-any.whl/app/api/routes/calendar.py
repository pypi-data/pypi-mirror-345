from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.models.calendar_event import CalendarEvent
from app.core.models.user import User
from app.api.dependencies import CurrentUser

from app.core.schemas.calendar_event import (
    CalendarEvent as CalendarEventSchema,
    CalendarEventCreate,
    CalendarEventUpdate,
)

from app.core.security import get_current_active_user
from app.db.session import get_db

router = APIRouter(prefix="/calendar", tags=["calendar"])

@router.get("/events", response_model=List[CalendarEventSchema])
def get_calendar_events(
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    event_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Получить список событий календаря текущего пользователя с возможностью фильтрации
    """
    query = db.query(CalendarEvent).filter(CalendarEvent.user_id == current_user.id)
    if start_date:
        query = query.filter(CalendarEvent.start_time >= start_date)
    if end_date:
        query = query.filter(CalendarEvent.start_time <= end_date)
    if event_type:
        query = query.filter(CalendarEvent.event_type == event_type)
    
    events = query.order_by(CalendarEvent.start_time).offset(skip).limit(limit).all()
    return events

@router.post("/events", response_model=CalendarEventSchema, status_code=status.HTTP_201_CREATED)
def create_calendar_event(
    current_user: CurrentUser,
    event_in: CalendarEventCreate,
    db: Session = Depends(get_db),
):
    """
    Создать новое событие календаря
    """
    end_time = event_in.end_time
    if not end_time and not event_in.all_day:
        end_time = event_in.start_time + timedelta(hours=1)
    
    event = CalendarEvent(
        title=event_in.title,
        description=event_in.description,
        start_time=event_in.start_time,
        end_time=end_time,
        all_day=event_in.all_day,
        location=event_in.location,
        event_type=event_in.event_type,
        user_id=current_user.id
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

@router.get("/events/{event_id}", response_model=CalendarEventSchema)
def get_calendar_event(
    event_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """
    Получить детали события календаря по ID
    """
    event = db.query(CalendarEvent).filter(
        CalendarEvent.id == event_id,
        CalendarEvent.user_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Событие календаря не найдено"
        )
    
    return event

@router.put("/events/{event_id}", response_model=CalendarEventSchema)
def update_calendar_event(
    current_user: CurrentUser,
    event_id: int,
    event_in: CalendarEventUpdate,
    db: Session = Depends(get_db)
):
    """
    Обновить событие календаря
    """
    event = db.query(CalendarEvent).filter(
        CalendarEvent.id == event_id,
        CalendarEvent.user_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Событие календаря не найдено"
        )
    
    # Обновляем поля события
    update_data = event_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    db.commit()
    db.refresh(event)
    return event

@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calendar_event(
    current_user: CurrentUser,
    event_id: int,
    db: Session = Depends(get_db)
):
    """
    Удалить событие календаря
    """
    event = db.query(CalendarEvent).filter(
        CalendarEvent.id == event_id,
        CalendarEvent.user_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Событие календаря не найдено"
        )
    
    db.delete(event)
    db.commit()
    return None
