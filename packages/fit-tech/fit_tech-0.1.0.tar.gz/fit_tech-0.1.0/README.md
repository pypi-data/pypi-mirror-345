# FitTech

# FitTech – Репозиторий фитнес-приложения

**FitTech** — это полный стек на базе FastAPI для трекинга фитнес-данных, управления тренировками, планирования питания, напоминаний и многого другого. Проект предоставляет надёжный backend-API и простой web-интерфейс на Jinja2/Bootstrap.

---

## Возможности

- **Аутентификация пользователей**: регистрация, вход (+ выход по JWT).  
- **Управление тренировками**: CRUD для тренировок и связанных упражнений.  
- **База упражнений**: добавление, редактирование, удаление упражнений.  
- **Управление рецептами**: хранение рецептов с ингредиентами и калориями.  
- **Планирование питания**: создание и управление планами приёма пищи.  
- **Напоминания**: настраиваемые напоминания (Celery + Redis).  
- **Интеграция с календарём**: просмотр событий и напоминаний.
В следующих обновлениях ожидается добавление следующих функций:
- **Чек-ины в залах**: трекинг визитов в зал.  
- **Геопоиск**: поиск ближайших залов (GeoAlchemy2 + Geopy).  
- **Интеграция с ИИ**: чат-бот-тренер на базе OpenAI.  
- **Web-интерфейс**: базовый фронтенд на Jinja2 + Bootstrap.

---
## Установка для пользователя
### 1. Установка пакета
pip install fit-tech

### 2. Создание .env
В корне проекта (или папке с кодом) создайте .env-файл:
``` bash
cat > .env <<EOF
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/fittech_db
SECRET_KEY=ваш_секрет
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
# TELEGRAM_BOT_TOKEN=...
# OPENAI_API_KEY=...
EOF
```
### 3. Запуск приложения
```bash
uvicorn fit_tech.main:app --reload --host 0.0.0.0 --port 8000
```
## Локальная разработка

Следуйте этим шагам, чтобы склонировать репозиторий, поднять окружение и установить все зависимости.

### 1. Клонирование репозитория

```bash
git clone https://github.com/your-org/fit-tech.git
cd fit-tech
```

---

### 2. Локальная разработка без Docker

#### 2.1 Виртуальное окружение

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 2.2 Установка зависимостей

* **Runtime-зависимости** (для запуска пакета):

  ```bash
  pip install --upgrade pip
  pip install .
  ```
* **Dev-зависимости** (тесты, линтеры, Alembic и т. д.):

  ```bash
  pip install -e ".[dev]"
  ```

#### 2.3 Переменные окружения
Отредактируйте .env:
#DATABASE_URL, SECRET_KEY, CELERY_BROKER_URL, CELERY_RESULT_BACKEND и т. д.

#### 2.4 Миграции базы данных

```bash
alembic upgrade head
```

Если миграции ещё не инициализированы:

```bash
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

#### 2.5 Запуск приложения

```bash
# Терминал 1: FastAPI-сервер
uvicorn fit_tech.main:app --reload

# Терминал 2: Celery-worker
celery -A fit_tech.workers.celery_app worker --loglevel=info
```
---

### 3. Работа через Docker и Docker Compose

Если вы хотите поднять всё окружение в контейнерах (PostgreSQL, Redis, веб-сервис, Celery):

1. **Скопируйте шаблон переменных окружения**
   Создайте `.env` и укажите реальные настройки (пароли, токены и т. д.).
   В `docker-compose.yml` переменные из `.env` будут подхвачены автоматически.

2. **Соберите и запустите контейнеры**

   ```bash
   docker-compose up --build
   ```
3. **Примените миграции**

   ```bash
   docker-compose exec web alembic upgrade head
   ```
4. **Остановка и удаление контейнеров**

   ```bash
   docker-compose down
   ```

---


