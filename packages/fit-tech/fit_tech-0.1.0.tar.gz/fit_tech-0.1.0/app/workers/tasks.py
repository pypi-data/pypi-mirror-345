from app.workers.celery_app import celery_app
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
import asyncio

import os
import openai
import requests
from app.db.session import get_db
from dateutil.rrule import rrulestr
from app.core.models.reminder import Reminder
from app.core.models.user import User
from app.core.models.workout import Workout

logger = logging.getLogger(__name__)

# Helper function to get a database session
async def get_session():
    """Get a database session for async operations in Celery tasks"""
    async_session = get_db()
    async with async_session() as session:
        yield session

@celery_app.task
def check_reminders():
    """
    Проверяет напоминания и отправляет уведомления для тех, 
    которые должны сработать в ближайшее время
    """
    try:
        logger.info("Проверка напоминаний...")
        
        # Run async code in a synchronous context
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(_check_reminders_async())
        
        return {
            "status": "success", 
            "checked_at": datetime.now().isoformat(),
            "reminders_found": result["count"]
        }
    except Exception as e:
        logger.error(f"Ошибка при проверке напоминаний: {e}")
        return {"status": "error", "error": str(e)}

async def _check_reminders_async():
    """Async implementation of reminder checking"""
    session_gen = get_session()
    session = await session_gen.__anext__()
    
    try:
        # Get current time and time window (next hour)
        now = datetime.now()
        next_hour = now + timedelta(hours=1)
        
        # Find active reminders that should trigger in the next hour
        query = select(Reminder).where(
            Reminder.is_active == True,
            Reminder.reminder_time >= now,
            Reminder.reminder_time <= next_hour
        )
        
        result = await session.execute(query)
        reminders = result.scalars().all()
        
        # Process each reminder (in a real app, this would send notifications)
        for reminder in reminders:
            logger.info(f"Processing reminder: {reminder.id} - {reminder.title}")
            # Here you would send notifications via email, push, etc.
            
        return {"count": len(reminders)}
    
    finally:
        await session.close()

@celery_app.task
def generate_workout_plan(user_id, goals, fitness_level):
    """
    Генерирует план тренировок на основе целей и уровня подготовки пользователя
    """
    try:
        logger.info(f"Генерация плана тренировок для пользователя {user_id}...")
        
        # Run async code in a synchronous context
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(_generate_workout_plan_async(user_id, goals, fitness_level))
        
        return {
            "status": "success", 
            "user_id": user_id,
            "workout_id": result.get("workout_id"),
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Ошибка при генерации плана тренировок: {e}")
        return {"status": "error", "error": str(e)}

async def _generate_workout_plan_async(user_id, goals, fitness_level):
    """Async implementation of workout plan generation"""
    session_gen = get_session()
    session = await session_gen.__anext__()
    
    try:
        # Check if user exists
        user_query = select(User).where(User.id == user_id)
        user_result = await session.execute(user_query)
        user = user_result.scalars().first()
        
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # In a real app, this would use more sophisticated logic based on goals and fitness level
        # For now, we'll create a simple workout
        workout = Workout(
            name=f"Workout Plan for {goals}",
            description=f"Auto-generated workout plan for {fitness_level} fitness level",
            type="strength" if "strength" in goals.lower() else "cardio",
            user_id=user_id,
            completed=False
        )
        
        session.add(workout)
        await session.commit()
        await session.refresh(workout)
        
        return {"workout_id": workout.id}
    
    finally:
        await session.close()

@celery_app.task
def process_user_analytics(user_id):
    """
    Обрабатывает аналитику пользователя и генерирует отчеты
    """
    try:
        logger.info(f"Обработка аналитики для пользователя {user_id}...")
        
        # Run async code in a synchronous context
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(_process_user_analytics_async(user_id))
        
        return {
            "status": "success", 
            "user_id": user_id,
            "stats": result.get("stats", {}),
            "processed_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Ошибка при обработке аналитики: {e}")
        return {"status": "error", "error": str(e)}

async def _process_user_analytics_async(user_id):
    """Async implementation of user analytics processing"""
    session_gen = get_session()
    session = await session_gen.__anext__()
    
    try:
        # Check if user exists
        user_query = select(User).where(User.id == user_id)
        user_result = await session.execute(user_query)
        user = user_result.scalars().first()
        
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Get workout statistics
        workouts_query = select(
            func.count(Workout.id).label("total"),
            func.count(Workout.id).filter(Workout.completed == True).label("completed")
        ).where(Workout.user_id == user_id)
        
        workouts_result = await session.execute(workouts_query)
        workout_stats = workouts_result.fetchone()
        
        # In a real app, you would gather more statistics and possibly store them
        stats = {
            "total_workouts": workout_stats.total if workout_stats else 0,
            "completed_workouts": workout_stats.completed if workout_stats else 0,
            "completion_rate": round(workout_stats.completed / workout_stats.total * 100, 2) if workout_stats and workout_stats.total > 0 else 0
        }
        
        return {"stats": stats}
    
    finally:
        await session.close()

# # Additional task for OpenAI integration
# @celery_app.task
# def generate_ai_workout_suggestion(user_id, preferences):
#     """
#     Использует OpenAI для генерации персонализированной тренировки
#     """
#     try:
#         logger.info(f"Генерация AI-рекомендаций для пользователя {user_id}...")
        
#         # In a real app, this would call OpenAI API
#         # For now, we'll simulate a response
#         suggestion = {
#             "workout_name": f"AI Suggested Workout for {preferences.get('goal', 'general fitness')}",
#             "description": f"This workout is designed for your {preferences.get('fitness_level', 'intermediate')} level",
#             "exercises": [
#                 {"name": "Squats", "sets": 3, "reps": 12},
#                 {"name": "Push-ups", "sets": 3, "reps": 10},
#                 {"name": "Plank", "sets": 3, "duration": "30 seconds"}
#             ]
#         }
        
#         return {
#             "status": "success", 
#             "user_id": user_id,
#             "suggestion": suggestion,
#             "generated_at": datetime.now().isoformat()
#         }
#     except Exception as e:
#         logger.error(f"Ошибка при генерации AI-рекомендаций: {e}")
#         return {"status": "error", "error": str(e)}


# Токен вашего бота из .env
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

@celery_app.task
def send_reminder(
    reminder_id: int,
    telegram_id: str,
    title: str,
    description: str,
    rrule: str | None = None,
    base_time_iso: str | None = None
):
    """
    Таск, который отправляет одно напоминание в Telegram.
    Если передан rrule и base_time_iso, то после отправки
    перепланирует следующий запуск.
    """
    if not TELEGRAM_TOKEN or not telegram_id:
        celery_app.logger.warning(f"[send_reminder] Пропущено: нет TELEGRAM_TOKEN или telegram_id")
        return

    text = f"*Напоминание:* {title}\n{description}"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": telegram_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        resp = requests.post(url, json=payload, timeout=5)
        resp.raise_for_status()
    except Exception as e:
        celery_app.logger.error(f"[send_reminder] Ошибка отправки: {e}")

    # Если есть правило повторения — запланировать следующее
    if rrule and base_time_iso:
        try:
            rule = rrulestr(rrule, dtstart=datetime.fromisoformat(base_time_iso))
            next_run: datetime | None = rule.after(datetime.utcnow(), inc=False)
            if next_run:
                schedule_reminder.apply_async(
                    args=[reminder_id, telegram_id, title, description, rrule, base_time_iso],
                    eta=next_run
                )
                celery_app.logger.info(f"[send_reminder] Запланировано следующее по RRULE: {next_run}")
        except Exception as e:
            celery_app.logger.error(f"[send_reminder] Не удалось перепланировать по RRULE: {e}")


@celery_app.task
def schedule_reminder(
    reminder_id: int,
    telegram_id: str,
    title: str,
    description: str,
    rrule: str | None = None,
    reminder_time_iso: str | None = None
):
    """
    Таск, который раз в API вызывается при создании/обновлении напоминания.
    Он вычисляет время первого (или следующего) срабатывания и планирует send_reminder.
    """
    if not reminder_time_iso:
        celery_app.logger.warning(f"[schedule_reminder] Пропущено: нет reminder_time_iso")
        return

    # время, на которое изначально назначено напоминание
    base_time = datetime.fromisoformat(reminder_time_iso)

    if rrule:
        # строка RRULE должна быть в формате iCal, например "FREQ=DAILY;INTERVAL=1"
        try:
            rule = rrulestr(rrule, dtstart=base_time)
            first_run = rule.after(datetime.utcnow(), inc=True)
        except Exception as e:
            celery_app.logger.error(f"[schedule_reminder] Ошибка парсинга RRULE: {e}")
            return
    else:
        first_run = base_time

    if not first_run:
        celery_app.logger.info(f"[schedule_reminder] Нет следующего времени по RRULE")
        return

    # Планируем таск на первое найденное время
    send_reminder.apply_async(
        args=[reminder_id, telegram_id, title, description, rrule, reminder_time_iso],
        eta=first_run
    )
    celery_app.logger.info(f"[schedule_reminder] Запланировано напоминание #{reminder_id} на {first_run}")

@celery_app.task
def process_openai_request(
    user_id: int,
    message: str,
    chat_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Запускается из /api/openai — отправляет запрос в OpenAI и возвращает ответ.
    """
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты — фитнес-тренер-ассистент."},
                {"role": "user",   "content": message},
            ],
        )
        answer = resp.choices[0].message.content
        result = {"answer": answer}
        if chat_id is not None:
            result["chat_id"] = chat_id
        return result
    except Exception as e:
        return {"answer": "Ошибка AI-сервиса, попробуйте позже.", "error": str(e)}


