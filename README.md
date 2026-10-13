# Wallet Service

REST API для работы с кошельками на FastAPI + PostgreSQL.

## Запуск

    cp .env.example .env       # Windows: Copy-Item .env.example .env
    docker compose up --build

- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

## API

### Получить баланс

    GET /api/v1/wallets/{wallet_uuid}

### Изменить баланс

    POST /api/v1/wallets/{wallet_uuid}/operation
    Content-Type: application/json

    {"operation_type": "DEPOSIT", "amount": 1000}
    {"operation_type": "WITHDRAW", "amount": 500}

Возможные ответы:
- 200 — новый баланс
- 400 — недостаточно средств
- 404 — кошелёк не найден
- 422 — ошибка валидации

## Тесты

    docker compose up -d db
    python -m venv .venv
    .venv\Scripts\Activate.ps1                        # Windows
    pip install -r requirements.txt
    $env:DATABASE_URL = "postgresql+asyncpg://wallet:wallet@localhost:5432/wallet"
    pytest -v

Ожидаемо: 8 passed.

## Конкурентность

Изменение баланса выполняется в транзакции с блокировкой строки
(`SELECT ... FOR UPDATE`), что исключает lost update при параллельных
запросах к одному и тому же кошельку. Отдельный тест
`test_concurrent_withdrawals` это проверяет: 100 параллельных списаний
по 1 руб из кошелька с балансом 50 → ровно 50 успешных и 50 ошибок,
итоговый баланс 0.

## Стек

- FastAPI (async)
- SQLAlchemy 2.0 (async) + asyncpg
- PostgreSQL 16
- Alembic (миграции)
- Pydantic v2
- pytest + pytest-asyncio + httpx
- Docker + docker-compose