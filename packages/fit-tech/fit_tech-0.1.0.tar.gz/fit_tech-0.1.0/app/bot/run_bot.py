import asyncio
import logging
from app.bot.bot import dp, bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """
    Основная функция для запуска бота
    """
    logger.info("Запуск Telegram бота...")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен")
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске бота: {e}")
