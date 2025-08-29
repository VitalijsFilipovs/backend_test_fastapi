# Backend Test — FastAPI + JWT

Простой API с регистрацией, логином (JWT), публичным/приватным эндпоинтами и SQLite.
Подойдёт как минимальный шаблон для тестового задания.

## Стек
- FastAPI
- SQLite + SQLAlchemy
- JWT (python-jose)
- Хеширование паролей (passlib[bcrypt])

## Быстрый старт (локально, Windows/PowerShell)
# 1) Переходим в папку проекта
cd backend_test_fastapi

# 2) Создаём виртуальное окружение (если ещё нет)
python -m venv .venv

# 3) Активируем окружение
# Если Activate.ps1 блокируется политикой скриптов, используйте .bat-версию:
.\.venv\Scripts\activate.bat

# 4) Устанавливаем зависимости приложения
pip install -r requirements.txt

# 5) (для тестов) Ставим dev-зависимости
pip install pytest httpx

# 6) Если ругается на EmailStr — доустановите extra для pydantic
pip install "pydantic[email]"

# 7) Прогоняем тесты
pytest -q
# Ожидаем: 1 passed (или больше, если добавите дополнительные тесты)

# Если тест/регистрация падает с "Email already registered",
# начните «с чистой» БД:
Remove-Item .\app.db -Force -ErrorAction SilentlyContinue

# 8) Настраиваем переменные окружения (опционально)
$env:JWT_SECRET = "supersecretkey"
$env:JWT_EXPIRE_MINUTES = "120"
$env:DB_URL = "sqlite:///./app.db"

# 9) Запускаем сервер
uvicorn app.main:app --reload
# Сервер доступен на http://127.0.0.1:8000 (Swagger: /docs)


Примечание: если используете Git Bash/WSL/macOS/Linux, активируйте окружение так:

source .venv/bin/activate

```

## Переменные окружения (опционально)
Вы можете задать **JWT_SECRET** и **JWT_EXPIRE_MINUTES** (по умолчанию секрет = `"CHANGE_ME"` и срок = 60 минут).
```bash
set JWT_SECRET=supersecretkey   # Windows PowerShell: $env:JWT_SECRET="supersecretkey"
set JWT_EXPIRE_MINUTES=120
```

## Эндпоинты
- `POST /register` — регистрация пользователя (email, password). Возвращает id и email.
- `POST /login` — логин, возвращает JWT.
- `GET /public-data` — публичные данные (без авторизации).
- `GET /private-data` — приватные данные (требуется Bearer JWT).
- `GET /health` — проверка живости сервиса.

### Примеры запросов (cURL)
Регистрация:
```bash
curl -X POST http://127.0.0.1:8000/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Secret123!"}'
```

Логин:
```bash
curl -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Secret123!"}'
# => {"access_token":"<JWT>","token_type":"bearer"}
```

Публичные данные:
```bash
curl http://127.0.0.1:8000/public-data
```

Приватные данные (нужен токен):
```bash
TOKEN="<вставьте_JWT_из_логина>"
curl http://127.0.0.1:8000/private-data -H "Authorization: Bearer $TOKEN"
```

## Структура
```text
backend_test_fastapi/
├─ app/
│  ├─ main.py          # точки входа + роуты
│  ├─ database.py      # подключение к БД
│  ├─ models.py        # SQLAlchemy модели
│  ├─ schemas.py       # Pydantic-схемы
│  ├─ auth.py          # создание/проверка JWT
│  ├─ utils.py         # хеширование паролей
│  └─ deps.py          # зависимости (current_user)
├─ tests/
│  └─ test_auth.py     # базовые тесты
└─ requirements.txt
```

## Тесты (pytest)
```bash
pip install pytest
pytest -q
```

## Обработка ошибок
- Неправильный логин/пароль → 401 Unauthorized
- Уже существующий email → 400 Bad Request
- Отсутствие или неверный JWT → 401 Unauthorized

## Примечания
- Для простоты используется SQLite-файл `app.db` в корне проекта.
- Для production обязательно смените `JWT_SECRET` и добавьте миграции, логи и т.д.

----------------------------------------------------------------------------------------
Запуск в Docker

Требуется установленный Docker (Compose v2). Переменные окружения берутся из файла .env.

1) Подготовка .env

Если в проекте есть .env.example, скопируйте его в .env:

# Linux/macOS
cp .env.example .env

# Windows PowerShell
Copy-Item .env.example .env


В .env по умолчанию используется SQLite:

DB_URL=sqlite:///./app.db
JWT_SECRET=supersecretkey
JWT_EXPIRE_MINUTES=120

2) Поднять сервис
docker compose up --build


После сборки API будет доступен:

Swagger UI: http://127.0.0.1:8000/docs

Healthcheck: http://127.0.0.1:8000/health

3) Хранение данных

В docker-compose.yml смонтирован volume:

volumes:
  - ./app.db:/app/app.db


Поэтому файл базы app.db хранится рядом с проектом на хосте и не теряется при перезапусках контейнера.

4) Остановка
# остановить и удалить контейнеры/сеть (без удаления образов и файла app.db)
docker compose down

5) Если порт 8000 занят

Измените маппинг порта в docker-compose.yml:

ports:
  - "8001:8000"   # было "8000:8000"


И используйте: http://127.0.0.1:8001/docs

6) Примеры запросов (в Docker)
# Регистрация
curl -X POST http://127.0.0.1:8000/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Secret123!"}'

# Логин (получить JWT)
curl -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Secret123!"}'

# Приватные данные
TOKEN="<JWT_из_логина>"
curl http://127.0.0.1:8000/private-data -H "Authorization: Bearer $TOKEN"
