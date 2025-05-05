# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Основные
    APP_NAME: str = "Fitness App"
    API_V1_STR: str = "/api"
    SECRET_KEY: str

    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    ALGORITHM: str = "HS256"

    # База данных
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # OpenAI / Telegram
    OPENAI_API_KEY: Optional[str] = None
    TELEGRAM_BOT_TOKEN: Optional[str] = None

    # Web‐app
    WEBAPP_BASE_URL: str = "http://localhost"

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    # .env
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra='ignore' 
    )
settings = Settings()

