from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.models.reminder import Reminder
from app.core.models.calendar_event import CalendarEvent
from app.core.models.user import User
from app.core.schemas.reminder import (
    Reminder as ReminderSchema,
    ReminderCreate,
    ReminderUpdate)
from app.core.schemas.calendar_event import (
    CalendarEvent as CalendarEventSchema,
    CalendarEventCreate,
    CalendarEventUpdate,
)

from app.api.dependencies import CurrentUser
from app.core.security import get_current_active_user
from app.db.session import get_db
from app.workers.tasks import schedule_reminder

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.get("/", response_model=List[ReminderSchema])
def get_reminders(
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """
    Получить список напоминаний текущего пользователя с возможностью фильтрации
    """
    query = db.query(Reminder).filter(Reminder.user_id == current_user.id)

    if is_active is not None:
        query = query.filter(Reminder.is_active == is_active)

    reminders = query.order_by(Reminder.datetime).offset(skip).limit(limit).all()
    return reminders


@router.post("/", response_model=ReminderSchema, status_code=status.HTTP_201_CREATED)
def create_reminder(
    current_user: CurrentUser,
    reminder_in: ReminderCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Создать новое напоминание
    """
    reminder = Reminder(
        title=reminder_in.title,
        description=reminder_in.description,
        datetime=reminder_in.datetime,
        rrule=reminder_in.rrule,
        is_active=reminder_in.is_active,
        user_id=current_user.id,
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)

    if reminder.is_active:
        background_tasks.add_task(
            schedule_reminder,
            reminder_id=reminder.id,
            user_id=current_user.id,
            telegram_id=current_user.telegram_id,
            title=reminder.title,
            description=reminder.description,
            reminder_time=reminder.datetime,
            rrule=reminder.rrule,
        )

    return reminder


@router.get("/{reminder_id}", response_model=ReminderSchema)
def get_reminder(
    reminder_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """
    Получить детали напоминания по ID
    """
    reminder = (
        db.query(Reminder)
        .filter(Reminder.id == reminder_id, Reminder.user_id == current_user.id)
        .first()
    )

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Напоминание не найдено"
        )

    return reminder


@router.put("/{reminder_id}", response_model=ReminderSchema)
def update_reminder(
    current_user: CurrentUser,
    reminder_id: int,
    reminder_in: ReminderUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Обновить напоминание
    """
    reminder = (
        db.query(Reminder)
        .filter(Reminder.id == reminder_id, Reminder.user_id == current_user.id)
        .first()
    )

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Напоминание не найдено"
        )

    update_data = reminder_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(reminder, field, value)

    db.commit()
    db.refresh(reminder)

    if reminder.is_active:
        background_tasks.add_task(
            schedule_reminder,
            reminder_id=reminder.id,
            user_id=current_user.id,
            telegram_id=current_user.telegram_id,
            title=reminder.title,
            description=reminder.description,
            reminder_time=reminder.datetime,
            rrule=reminder.rrule,
        )

    return reminder


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reminder(
    reminder_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """
    Удалить напоминание
    """
    reminder = (
        db.query(Reminder)
        .filter(Reminder.id == reminder_id, Reminder.user_id == current_user.id)
        .first()
    )

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Напоминание не найдено"
        )

    db.delete(reminder)
    db.commit()
    return None
