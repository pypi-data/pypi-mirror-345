import logging
import asyncio
import os
import httpx
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, Message, InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not API_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN не найден в переменных окружения! Запуск невозможен.")
    exit(1)

WEBAPP_BASE_URL = os.getenv("WEBAPP_BASE_URL", "http://127.0.0.1:8000")
API_V1_STR = "/api"

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class RegistrationStates(StatesGroup):
    awaiting_email = State()
    awaiting_username = State()
    awaiting_password = State()

class LoginStates(StatesGroup):
    awaiting_email = State()
    awaiting_password = State()

class WorkoutStates(StatesGroup):
    choosing_action = State()
    viewing_list = State()
    viewing_detail = State()

class RecipeStates(StatesGroup):
    choosing_action = State()
    viewing_list = State()
    viewing_detail = State()

class ReminderStates(StatesGroup):
    choosing_action = State()
    viewing_list = State()
    viewing_detail = State()

async def make_api_request(method: str, endpoint: str, token: Optional[str] = None, **kwargs) -> httpx.Response:
    """Отправляет асинхронный запрос к API веб-приложения."""
    url = f"{WEBAPP_BASE_URL}{API_V1_STR}{endpoint}"
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.request(method, url, headers=headers, **kwargs)
            logger.info(f"API Request: {method} {url} - Status: {response.status_code}")
            return response
        except httpx.RequestError as e:
            logger.error(f"API Request Error: {method} {url} - Error: {e}")
            raise

async def require_auth(message: types.Message, state: FSMContext) -> str | None:
    """Проверяет, авторизован ли пользователь, и возвращает токен."""
    telegram_id = str(message.from_user.id)
    user_data = await state.get_data()
    if user_data and "token" in user_data:
        return user_data["token"]
    else:
        await message.answer("Эта команда требует авторизации. Пожалуйста, войдите с помощью /login или зарегистрируйтесь /register.")
        return None

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    logging.info(f"Получена команда /start от пользователя {message.from_user.id}")
    await message.answer(
        "Привет! Я бот фитнес-приложения FitTech. \n"
        "Я помогу тебе управлять тренировками, питанием и напоминаниями.\n\n"
        "Используйте следующие команды:\n"
        "/help - Справка по командам\n"
        "/register - Регистрация нового пользователя\n"
        "/login - Авторизация существующего пользователя\n"
        "/workouts - Управление тренировками (нужна авторизация)\n"
        "/recipes - Управление рецептами (нужна авторизация)\n"
        "/reminders - Управление напоминаниями (нужна авторизация)\n"
        # "/mealplans - Управление планами питания (в разработке)\n"
        # "/coach - Чат с виртуальным тренером (скоро)"
    )

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    logging.info(f"Получена команда /help от пользователя {message.from_user.id}")
    await message.answer(
        "Доступные команды:\n"
        "/start - Начало работы с ботом\n"
        "/help - Справка по командам\n"
        "/register - Регистрация нового пользователя\n"
        "/login - Авторизация существующего пользователя\n"
        "/workouts - Просмотр и управление тренировками\n"
        "/recipes - Просмотр и управление рецептами\n"
        "/reminders - Просмотр и управление напоминаниями\n"
        # "/mealplans - Управление планами питания (в разработке)\n"
        # "/coach - Чат с виртуальным тренером"
    )

@dp.message(Command("register"))
async def cmd_register(message: types.Message, state: FSMContext):
    logging.info(f"Получена команда /register от пользователя {message.from_user.id}")
    await message.answer("Начинаем регистрацию. Пожалуйста, введите ваш email:")
    await state.set_state(RegistrationStates.awaiting_email)

@dp.message(RegistrationStates.awaiting_email)
async def process_email_register(message: types.Message, state: FSMContext):
    email = message.text
    await state.update_data(email=email)
    await message.answer("Отлично! Теперь введите желаемое имя пользователя (username):")
    await state.set_state(RegistrationStates.awaiting_username)

@dp.message(RegistrationStates.awaiting_username)
async def process_username_register(message: types.Message, state: FSMContext):
    username = message.text
    await state.update_data(username=username)
    await message.answer("Хорошо. Теперь придумайте и введите пароль:")
    await state.set_state(RegistrationStates.awaiting_password)

@dp.message(RegistrationStates.awaiting_password)
async def process_password_register(message: types.Message, state: FSMContext):
    password = message.text
    user_data = await state.get_data()
    email = user_data.get("email")
    username = user_data.get("username")
    telegram_id = str(message.from_user.id)

    await message.answer("Регистрирую вас... Пожалуйста, подождите.")

    try:
        response = await make_api_request(
            "POST",
            "/auth/signup",
            json={
                "email": email,
                "username": username,
                "password": password,
                "telegram_id": telegram_id
            }
        )

        if response.status_code == 200 or response.status_code == 201:
            await message.answer(f"Регистрация прошла успешно! Ваш email: {email}, username: {username}.\nТеперь вы можете войти с помощью команды /login.")
            await state.clear()
        elif response.status_code == 400:
            error_detail = response.json().get("detail", "Неизвестная ошибка валидации.")
            if "already exists" in str(error_detail).lower():
                 await message.answer(f"Ошибка регистрации: Пользователь с таким email или username уже существует. Попробуйте /login или используйте другие данные для /register.")
            else:
                await message.answer(f"Ошибка регистрации: {error_detail}\nПопробуйте еще раз /register")
            await state.clear()
        else:
            await message.answer(f"Произошла ошибка при регистрации (Код: {response.status_code}). Попробуйте позже.")
            logger.error(f"Ошибка API регистрации: {response.status_code} - {response.text}")
            await state.clear()

    except httpx.RequestError as e:
        await message.answer("Не удалось связаться с сервером регистрации. Попробуйте позже.")
        await state.clear()
    except Exception as e:
        logger.exception(f"Непредвиденная ошибка при регистрации пользователя {telegram_id}")
        await message.answer("Произошла внутренняя ошибка. Попробуйте позже.")
        await state.clear()

@dp.message(Command("login"))
async def cmd_login(message: types.Message, state: FSMContext):
    logging.info(f"Получена команда /login от пользователя {message.from_user.id}")
    await message.answer("Для входа введите ваш email:")
    await state.set_state(LoginStates.awaiting_email)

@dp.message(LoginStates.awaiting_email)
async def process_email_login(message: types.Message, state: FSMContext):
    email = message.text
    await state.update_data(email=email)
    await message.answer("Теперь введите ваш пароль:")
    await state.set_state(LoginStates.awaiting_password)

@dp.message(LoginStates.awaiting_password)
async def process_password_login(message: types.Message, state: FSMContext):
    password = message.text
    user_data = await state.get_data()
    email = user_data.get("email")
    telegram_id = str(message.from_user.id)

    await message.answer("Выполняю вход... Пожалуйста, подождите.")

    try:
        response = await make_api_request(
            "POST",
            "/auth/login",
            data={"username": email, "password": password}
        )

        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            await state.update_data(token=access_token)
            logger.info(f"Пользователь {telegram_id} ({email}) успешно вошел.")
            await message.answer("Вход выполнен успешно! Теперь вам доступны команды управления.")
            await state.set_state(None)

        elif response.status_code == 401:
            await message.answer("Ошибка входа: Неверный email или пароль. Попробуйте еще раз /login")
            await state.clear()
        else:
            await message.answer(f"Произошла ошибка при входе (Код: {response.status_code}). Попробуйте позже.")
            logger.error(f"Ошибка API логина: {response.status_code} - {response.text}")
            await state.clear()

    except httpx.RequestError as e:
        await message.answer("Не удалось связаться с сервером аутентификации. Попробуйте позже.")
        await state.clear()
    except Exception as e:
        logger.exception(f"Непредвиденная ошибка при логине пользователя {telegram_id}")
        await message.answer("Произошла внутренняя ошибка. Попробуйте позже.")
        await state.clear()

@dp.message(Command("workouts"))
async def cmd_workouts(message: types.Message, state: FSMContext):
    token = await require_auth(message, state)
    if not token:
        return
    logging.info(f"Получена команда /workouts от пользователя {message.from_user.id}")

    try:
        response = await make_api_request("GET", "/workouts/", token=token, params={"limit": 10})

        if response.status_code == 200:
            workouts = response.json()
            if not workouts:
                await message.answer("У вас пока нет сохраненных тренировок. Вы можете добавить их через веб-интерфейс.")
                return

            response_text = "Ваши последние тренировки:\n\n"
            buttons = []
            for workout in workouts:
                workout_id = workout.get("id")
                name = workout.get("name", "Без названия")
                workout_type = workout.get("type", "Не указан")
                response_text += f"- {name} (Тип: {workout_type})\n"
                buttons.append([InlineKeyboardButton(text=f"{name}", callback_data=f"workout_view_{workout_id}")])

            response_text += "\nНажмите на тренировку для просмотра деталей."
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            await message.answer(response_text, reply_markup=keyboard)
            await state.set_state(WorkoutStates.viewing_list)

        elif response.status_code == 401:
            await message.answer("Ваша сессия истекла. Пожалуйста, войдите снова /login.")
            await storage.delete_data(bot, key=f"user_token_{str(message.from_user.id)}")
        else:
            await message.answer(f"Не удалось получить список тренировок (Ошибка: {response.status_code}). Попробуйте позже.")
            logger.error(f"Ошибка API /workouts: {response.status_code} - {response.text}")

    except httpx.RequestError:
        await message.answer("Не удалось связаться с сервером. Попробуйте позже.")
    except Exception as e:
        logger.exception(f"Ошибка при обработке /workouts для {message.from_user.id}")
        await message.answer("Произошла внутренняя ошибка. Попробуйте позже.")

@dp.callback_query(WorkoutStates.viewing_list, F.data.startswith("workout_view_"))
async def cq_view_workout_detail(callback_query: types.CallbackQuery, state: FSMContext):
    workout_id = int(callback_query.data.split("_")[-1])
    token = await require_auth(callback_query.message, state)
    if not token:
        await callback_query.answer("Требуется авторизация.", show_alert=True)
        return

    await callback_query.message.edit_text("Загружаю детали тренировки...")

    try:
        response = await make_api_request("GET", f"/workouts/{workout_id}", token=token)

        if response.status_code == 200:
            workout = response.json()
            name = workout.get("name", "Без названия")
            workout_type = workout.get("type", "Не указан")
            description = workout.get("description", "Нет описания")
            exercises = workout.get("exercises", [])

            response_text = f"*Тренировка: {name}*\n"
            response_text += f"Тип: {workout_type}\n"
            response_text += f"Описание: {description}\n\n"
            if exercises:
                response_text += "*Упражнения:*\n"
                for ex in exercises:
                    ex_name = ex.get("exercise", {}).get("name", "Упражнение")
                    sets = ex.get("sets", "-")
                    reps = ex.get("reps", "-")
                    response_text += f" - {ex_name}: {sets} подходов x {reps} повторений\n"
            else:
                response_text += "Упражнения не добавлены.\n"

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="< Назад к списку", callback_data="workouts_back_to_list")]
            ])
            await callback_query.message.edit_text(response_text, reply_markup=keyboard, parse_mode="Markdown")
            await state.set_state(WorkoutStates.viewing_detail)

        elif response.status_code == 404:
            await callback_query.message.edit_text("Тренировка не найдена.")
            await state.set_state(WorkoutStates.choosing_action)
        elif response.status_code == 401:
            await callback_query.message.answer("Ваша сессия истекла. Пожалуйста, войдите снова /login.")
            await storage.delete_data(bot, key=f"user_token_{str(callback_query.from_user.id)}")
            await state.clear()
        else:
            await callback_query.message.edit_text(f"Ошибка загрузки деталей (Код: {response.status_code}).")
            logger.error(f"Ошибка API /workouts/{workout_id}: {response.status_code} - {response.text}")
            await state.set_state(WorkoutStates.choosing_action)

    except httpx.RequestError:
        await callback_query.message.edit_text("Не удалось связаться с сервером.")
        await state.set_state(WorkoutStates.choosing_action)
    except Exception as e:
        logger.exception(f"Ошибка при просмотре деталей тренировки {workout_id} для {callback_query.from_user.id}")
        await callback_query.message.edit_text("Произошла внутренняя ошибка.")
        await state.set_state(WorkoutStates.choosing_action)

    await callback_query.answer()

@dp.callback_query(WorkoutStates.viewing_detail, F.data == "workouts_back_to_list")
async def cq_workouts_back_to_list(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await cmd_workouts(callback_query.message, state)
    await callback_query.answer()

@dp.message(Command("recipes"))
async def cmd_recipes(message: types.Message, state: FSMContext):
    token = await require_auth(message, state)
    if not token:
        return
    logging.info(f"Получена команда /recipes от пользователя {message.from_user.id}")

    try:
        response = await make_api_request("GET", "/recipes/", token=token, params={"limit": 10})

        if response.status_code == 200:
            recipes = response.json()
            if not recipes:
                await message.answer("У вас пока нет сохраненных рецептов. Вы можете добавить их через веб-интерфейс.")
                return

            response_text = "Ваши последние рецепты:\n\n"
            buttons = []
            for recipe in recipes:
                recipe_id = recipe.get("id")
                name = recipe.get("name", "Без названия")
                response_text += f"- {name}\n"
                buttons.append([InlineKeyboardButton(text=f"{name}", callback_data=f"recipe_view_{recipe_id}")])

            response_text += "\nНажмите на рецепт для просмотра деталей."
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            await message.answer(response_text, reply_markup=keyboard)
            await state.set_state(RecipeStates.viewing_list)

        elif response.status_code == 401:
            await message.answer("Ваша сессия истекла. Пожалуйста, войдите снова /login.")
            await storage.delete_data(bot, key=f"user_token_{str(message.from_user.id)}")
        else:
            await message.answer(f"Не удалось получить список рецептов (Ошибка: {response.status_code}). Попробуйте позже.")
            logger.error(f"Ошибка API /recipes: {response.status_code} - {response.text}")

    except httpx.RequestError:
        await message.answer("Не удалось связаться с сервером. Попробуйте позже.")
    except Exception as e:
        logger.exception(f"Ошибка при обработке /recipes для {message.from_user.id}")
        await message.answer("Произошла внутренняя ошибка. Попробуйте позже.")

@dp.callback_query(RecipeStates.viewing_list, F.data.startswith("recipe_view_"))
async def cq_view_recipe_detail(callback_query: types.CallbackQuery, state: FSMContext):
    recipe_id = int(callback_query.data.split("_")[-1])
    token = await require_auth(callback_query.message)
    if not token:
        await callback_query.answer("Требуется авторизация.", show_alert=True)
        return

    await callback_query.message.edit_text("Загружаю детали рецепта...")

    try:
        response = await make_api_request("GET", f"/recipes/{recipe_id}", token=token)

        if response.status_code == 200:
            recipe = response.json()
            name = recipe.get("name", "Без названия")
            description = recipe.get("description", "Нет описания")
            instructions = recipe.get("instructions", "Нет инструкций")
            ingredients = recipe.get("ingredients", [])
            cuisine = recipe.get("cuisine")
            meal_type = recipe.get("meal_type")
            calories = recipe.get("calories")
            protein = recipe.get("protein")
            fat = recipe.get("fat")
            carbs = recipe.get("carbs")
            prep_time = recipe.get("preparation_time")

            response_text = f"*Рецепт: {name}*\n"
            if cuisine: response_text += f"Кухня: {cuisine}\n"
            if meal_type: response_text += f"Тип блюда: {meal_type}\n"
            if prep_time: response_text += f"Время готовки: {prep_time} мин\n"
            if calories: response_text += f"КБЖУ: {calories} ккал / {protein}г / {fat}г / {carbs}г\n"
            response_text += f"\n*Описание:*\n{description}\n"

            if ingredients:
                response_text += "\n*Ингредиенты:*\n"
                for ing in ingredients:
                    ing_name = ing.get("ingredient", {}).get("name", "Ингредиент")
                    quantity = ing.get("quantity", "")
                    unit = ing.get("unit", "")
                    response_text += f" - {ing_name}: {quantity} {unit}\n"
            
            response_text += f"\n*Инструкции:*\n{instructions}\n"

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="< Назад к списку", callback_data="recipes_back_to_list")]
            ])
            if len(response_text) > 4090:
                response_text = response_text[:4090] + "..."
            await callback_query.message.edit_text(response_text, reply_markup=keyboard, parse_mode="Markdown")
            await state.set_state(RecipeStates.viewing_detail)

        elif response.status_code == 404:
            await callback_query.message.edit_text("Рецепт не найден.")
            await state.set_state(RecipeStates.choosing_action)
        elif response.status_code == 401:
            await callback_query.message.answer("Ваша сессия истекла. Пожалуйста, войдите снова /login.")
            await storage.delete_data(bot, key=f"user_token_{str(callback_query.from_user.id)}")
            await state.clear()
        else:
            await callback_query.message.edit_text(f"Ошибка загрузки деталей (Код: {response.status_code}).")
            logger.error(f"Ошибка API /recipes/{recipe_id}: {response.status_code} - {response.text}")
            await state.set_state(RecipeStates.choosing_action)

    except httpx.RequestError:
        await callback_query.message.edit_text("Не удалось связаться с сервером.")
        await state.set_state(RecipeStates.choosing_action)
    except Exception as e:
        logger.exception(f"Ошибка при просмотре деталей рецепта {recipe_id} для {callback_query.from_user.id}")
        await callback_query.message.edit_text("Произошла внутренняя ошибка.")
        await state.set_state(RecipeStates.choosing_action)

    await callback_query.answer()

@dp.callback_query(RecipeStates.viewing_detail, F.data == "recipes_back_to_list")
async def cq_recipes_back_to_list(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await cmd_recipes(callback_query.message, state)
    await callback_query.answer()

@dp.message(Command("reminders"))
async def cmd_reminders(message: types.Message, state: FSMContext):
    token = await require_auth(message, state)
    if not token:
        return
    logging.info(f"Получена команда /reminders от пользователя {message.from_user.id}")

    try:
        response = await make_api_request("GET", "/reminders/", token=token, params={"limit": 10, "is_active": True})

        if response.status_code == 200:
            reminders = response.json()
            if not reminders:
                await message.answer("У вас пока нет активных напоминаний. Вы можете добавить их через веб-интерфейс.")
                return

            response_text = "Ваши активные напоминания:\n\n"
            buttons = []
            for reminder in reminders:
                reminder_id = reminder.get("id")
                title = reminder.get("title", "Без названия")
                dt_str = reminder.get("datetime", "")
                try:
                    if dt_str.endswith("Z"):
                        dt_str = dt_str[:-1] + "+00:00"
                    dt_obj = datetime.fromisoformat(dt_str)
                    dt_formatted = dt_obj.strftime("%Y-%m-%d %H:%M")
                except ValueError:
                    dt_formatted = dt_str

                response_text += f"- {title} ({dt_formatted})\n"
                buttons.append([InlineKeyboardButton(text=f"{title} ({dt_formatted})", callback_data=f"reminder_view_{reminder_id}")])

            response_text += "\nНажмите на напоминание для просмотра деталей."
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            await message.answer(response_text, reply_markup=keyboard)
            await state.set_state(ReminderStates.viewing_list)

        elif response.status_code == 401:
            await message.answer("Ваша сессия истекла. Пожалуйста, войдите снова /login.")
            await storage.delete_data(bot, key=f"user_token_{str(message.from_user.id)}")
        else:
            await message.answer(f"Не удалось получить список напоминаний (Ошибка: {response.status_code}). Попробуйте позже.")
            logger.error(f"Ошибка API /reminders: {response.status_code} - {response.text}")

    except httpx.RequestError:
        await message.answer("Не удалось связаться с сервером. Попробуйте позже.")
    except Exception as e:
        logger.exception(f"Ошибка при обработке /reminders для {message.from_user.id}")
        await message.answer("Произошла внутренняя ошибка. Попробуйте позже.")


@dp.callback_query(ReminderStates.viewing_list, F.data.startswith("reminder_view_"))
async def cq_view_reminder_detail(callback_query: types.CallbackQuery, state: FSMContext):
    reminder_id = int(callback_query.data.split("_")[-1])
    token = await require_auth(callback_query.message)
    if not token:
        await callback_query.answer("Требуется авторизация.", show_alert=True)
        return

    await callback_query.message.edit_text("Загружаю детали напоминания...")

    try:
        response = await make_api_request("GET", f"/reminders/{reminder_id}", token=token)

        if response.status_code == 200:
            reminder = response.json()
            title = reminder.get("title", "Без названия")
            description = reminder.get("description", "Нет описания")
            dt_str = reminder.get("datetime", "")
            rrule = reminder.get("rrule")
            is_active = reminder.get("is_active", True)

            try:
                if dt_str.endswith("Z"):
                    dt_str = dt_str[:-1] + "+00:00"
                dt_obj = datetime.fromisoformat(dt_str)
                dt_formatted = dt_obj.strftime("%Y-%m-%d %H:%M (%Z)")
            except ValueError:
                dt_formatted = dt_str

            response_text = f"*Напоминание: {title}*\n"
            response_text += f"Время: {dt_formatted}\n"
            response_text += f"Статус: {'Активно' if is_active else 'не активно'}\n"
            if rrule:
                response_text += f"Повторение: {rrule}\n"
            response_text += f"\n*Описание:*\n{description}\n"

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="< Назад к списку", callback_data="reminders_back_to_list")]
            ])
            await callback_query.message.edit_text(response_text, reply_markup=keyboard, parse_mode="Markdown")
            await state.set_state(ReminderStates.viewing_detail)

        elif response.status_code == 404:
            await callback_query.message.edit_text("Напоминание не найдено.")
            await state.set_state(ReminderStates.choosing_action)
        elif response.status_code == 401:
            await callback_query.message.answer("Ваша сессия истекла. Пожалуйста, войдите снова /login.")
            await storage.delete_data(bot, key=f"user_token_{str(callback_query.from_user.id)}")
            await state.clear()
        else:
            await callback_query.message.edit_text(f"Ошибка загрузки деталей (Код: {response.status_code}).")
            logger.error(f"Ошибка API /reminders/{reminder_id}: {response.status_code} - {response.text}")
            await state.set_state(ReminderStates.choosing_action)

    except httpx.RequestError:
        await callback_query.message.edit_text("Не удалось связаться с сервером.")
        await state.set_state(ReminderStates.choosing_action)
    except Exception as e:
        logger.exception(f"Ошибка при просмотре деталей напоминания {reminder_id} для {callback_query.from_user.id}")
        await callback_query.message.edit_text("Произошла внутренняя ошибка.")
        await state.set_state(ReminderStates.choosing_action)

    await callback_query.answer()

@dp.callback_query(ReminderStates.viewing_detail, F.data == "reminders_back_to_list")
async def cq_reminders_back_to_list(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await cmd_reminders(callback_query.message, state)
    await callback_query.answer()

@dp.message(Command("mealplans"))
async def cmd_mealplans(message: types.Message):
    token = await require_auth(message)
    if not token:
        return
    logging.info(f"Получена команда /mealplans от пользователя {message.from_user.id}")
    await message.answer("Функционал управления планами питания пока не реализован в боте.")

@dp.message(StateFilter(None))
async def echo_outside_state(message: types.Message):
    if message.text and message.text.startswith("/"):
        logging.warning(f"Command 	'{message.text}	' was caught by echo handler outside state. Check handler registration order.")
        return

    logging.info(f"Получено сообщение вне состояния от пользователя {message.from_user.id}: {message.text}")
    await message.answer(f"Я не понимаю это сообщение: 	'{message.text}	'\nИспользуйте /help для просмотра доступных команд.")

async def main():
    logger.info("Запуск Telegram бота (локально)...")
    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен")
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске бота: {e}")

