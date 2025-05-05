import app.core.models

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from datetime import datetime

from app.api.routes import auth, workouts, exercises, recipes, ingredients, reminders, calendar, gyms, openai
from app.db.session import engine, Base
from app.core.config import settings

app = FastAPI(title="Fitness App API", version="1.0.0")

# Инициализация базы данных
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Настройка шаблонов Jinja2
templates = Jinja2Templates(directory="app/templates")

# Регистрация API-маршрутов
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(workouts.router, prefix="/api/workouts", tags=["workouts"])
app.include_router(exercises.router, prefix="/api/exercises", tags=["exercises"])
app.include_router(recipes.router, prefix="/api/recipes", tags=["recipes"])
app.include_router(ingredients.router, prefix="/api/ingredients", tags=["ingredients"])
app.include_router(reminders.router, prefix="/api/reminders", tags=["reminders"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["calendar"])
app.include_router(gyms.router, prefix="/api/gyms", tags=["gyms"])
app.include_router(openai.router, prefix="/api/openai", tags=["openai"])

@app.get("/")
async def index(request: Request):
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        print(f"Ошибка при рендеринге шаблона index.html: {e}")
        return {"message": "Ошибка при рендеринге шаблона", "error": str(e)}

@app.get("/login")
async def login_page(request: Request):
    try:
        return templates.TemplateResponse("login.html", {"request": request})
    except Exception as e:
        print(f"Ошибка при рендеринге шаблона login.html: {e}")
        return {"message": "Ошибка при рендеринге шаблона", "error": str(e)}

@app.get("/register")
async def register_page(request: Request):
    try:
        return templates.TemplateResponse("register.html", {"request": request})
    except Exception as e:
        print(f"Ошибка при рендеринге шаблона register.html: {e}")
        return {"message": "Ошибка при рендеринге шаблона", "error": str(e)}

@app.get("/workouts")
async def workouts_page(request: Request):
    try:
        return templates.TemplateResponse("workouts.html", {"request": request})
    except Exception as e:
        print(f"Ошибка при рендеринге шаблона workouts.html: {e}")
        return {"message": "Ошибка при рендеринге шаблона", "error": str(e)}

@app.get("/workouts/{workout_id}")
async def workout_detail(request: Request, workout_id: int):
    workout_data = {
        "id": workout_id,
        "name": f"Тренировка {workout_id}",
        "type": "Тип Заглушка",
        "description": "Описание Заглушка.",
        "exercises": [{"id": 1, "name": "Упражнение A"}, {"id": 2, "name": "Упражнение B"}]
    }
    try:
        return templates.TemplateResponse("workout_detail.html", {"request": request, "workout": workout_data})
    except Exception as e:
        print(f"Ошибка при рендеринге шаблона workout_detail.html: {e}")
        return {"message": "Ошибка при рендеринге шаблона", "error": str(e)}

@app.get("/recipes")
async def recipes_page(request: Request):
    try:
        return templates.TemplateResponse("recipes.html", {"request": request})
    except Exception as e:
        print(f"Ошибка при рендеринге шаблона recipes.html: {e}")
        return {"message": "Ошибка при рендеринге шаблона", "error": str(e)}

@app.get("/kcal-calculator")
async def kcal_calculator(request: Request):
    try:
        return templates.TemplateResponse("kcal_calculator.html", {"request": request})
    except Exception as e:
        print(f"Ошибка при рендеринге шаблона kcal_calculator.html: {e}")
        return {"message": "Ошибка при рендеринге шаблона", "error": str(e)}

@app.get("/reminders")
async def reminders_page(request: Request):
    try:
        return templates.TemplateResponse("reminders.html", {"request": request})
    except Exception as e:
        print(f"Ошибка при рендеринге шаблона reminders.html: {e}")
        return {"message": "Ошибка при рендеринге шаблона", "error": str(e)}

@app.get("/api/")
async def api_root():
    return {"message": "Fitness App API is running"}

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Тестовый маршрут для проверки шаблонов
@app.get("/test")
async def test_page(request: Request):
    try:
        return templates.TemplateResponse("test.html", {"request": request})
    except Exception as e:
        print(f"Ошибка при рендеринге тестового шаблона: {e}")
        return {"message": "Ошибка при рендеринге тестового шаблона", "error": str(e)}

