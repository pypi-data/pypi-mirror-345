# Исправленный файл для Celery
# app/workers/celery_app.py

from celery import Celery
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "app.workers",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.workers.tasks"]
)

# Оптимизированные настройки
celery_app.conf.update(
    worker_prefetch_multiplier=1,  # Предотвращает перегрузку воркеров
    task_acks_late=True,  # Подтверждение задачи только после успешного выполнения
    task_reject_on_worker_lost=True,  # Перезапуск задач при потере воркера
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_max_tasks_per_child=1000,  # Перезапуск воркера после 1000 задач
    task_soft_time_limit=300,  # Мягкий таймаут задачи (5 минут)
    task_time_limit=600,  # Жесткий таймаут задачи (10 минут)
    broker_transport_options={
        "visibility_timeout": 3600,  # 1 час
        "max_retries": 3,
    },
    result_expires=86400,  # Результаты хранятся 1 день
)
