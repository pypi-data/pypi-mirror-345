# app/db/session.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.models.base import Base

# URL из .env (compose прокидывает DATABASE_URL)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/fitness_app"
)
ASYNC_DATABASE_URL = DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
)

# создаём асинхронный движок
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    future=True
)

# **Здесь** нужно определить AsyncSessionLocal
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Генератор сессий для Depends
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


