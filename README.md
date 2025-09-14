# Contacts API

REST API для управління контактами з аутентифікацією, авторизацією та розширеними функціями.

## Нові функції

- ✅ **Sphinx документація** - автоматична генерація документації з docstrings
- ✅ **Модульне тестування** - покриття CRUD операцій та аутентифікації
- ✅ **Інтеграційне тестування** - тестування API ендпоінтів
- ✅ **Покриття тестами >75%** - контроль якості коду
- ✅ **Redis кешування** - кешування користувачів для швидкості
- ✅ **Скидання пароля** - безпечний механізм відновлення пароля
- ✅ **Ролі користувачів** - система ролей user/admin
- ✅ **Refresh токени** - пара access/refresh токенів

## Встановлення

1. Клонуйте репозиторій:
```bash
git clone <repository-url>
cd goit-pythonweb-hw-012
```

2. Встановіть залежності:
```bash
make install
# або
pip install -r requirements.txt
```

3. Створіть файл `.env`:
```env
DATABASE_URL=postgresql://user:password@localhost/contacts_db
REDIS_HOST=localhost
REDIS_PORT=6379
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
```

## Запуск

### Локально
```bash
make run-local
# або
uvicorn src.contacts_api.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker
```bash
make docker-up
# або
docker-compose up --build
```

## Тестування

### Запуск тестів
```bash
make test
# або
pytest
```

### Покриття тестами
```bash
make test-coverage
# або
pytest --cov=src/contacts_api --cov-report=html --cov-report=term-missing
```

## Документація

### Генерація документації
```bash
make docs
# або
cd docs && sphinx-build -b html . _build/html
```

### Перегляд документації
Відкрийте `docs/_build/html/index.html` у браузері

### Swagger документація
- Локально: http://localhost:8000/docs
- Docker: http://localhost:8001/docs

## API Endpoints

### Аутентифікація
- `POST /auth/register` - Реєстрація користувача
- `POST /auth/login` - Вхід користувача (повертає access + refresh токени)
- `GET /auth/verify-email/{token}` - Верифікація email
- `POST /auth/password-reset` - Запит на скидання пароля
- `POST /auth/password-reset/confirm` - Підтвердження скидання пароля

### Користувачі
- `GET /users/me` - Інформація про поточного користувача (rate limited)
- `PATCH /users/me/avatar` - Оновлення аватара (тільки admin)

### Контакти
- `POST /contacts/` - Створити контакт
- `GET /contacts/` - Список контактів (з пошуком: `?search=query`)
- `GET /contacts/{id}` - Контакт за ID
- `PUT /contacts/{id}` - Оновити контакт
- `DELETE /contacts/{id}` - Видалити контакт
- `GET /contacts/birthdays/upcoming` - Дні народження на наступні 7 днів

## Архітектура

```
src/contacts_api/
├── main.py              # FastAPI додаток та роути
├── models.py            # SQLAlchemy моделі
├── schemas.py           # Pydantic схеми
├── crud.py              # CRUD операції
├── auth.py              # Аутентифікація та авторизація
├── database.py          # Конфігурація бази даних
├── redis_cache.py       # Redis кешування
├── email_service.py     # Email сервіс
├── cloudinary_service.py # Cloudinary сервіс
└── migrate.py           # Міграції бази даних

tests/
├── conftest.py          # Конфігурація тестів
├── test_crud.py         # Модульні тести CRUD
├── test_auth.py         # Модульні тести аутентифікації
└── test_api.py          # Інтеграційні тести API

docs/
├── conf.py              # Конфігурація Sphinx
├── index.rst            # Головна сторінка документації
└── modules.rst          # Модулі документації
```

## Особливості

### Redis кешування
- Користувачі кешуються після першого запиту
- Кеш автоматично інвалідується при оновленні користувача
- TTL: 1 година

### Система ролей
- **user**: стандартний користувач
- **admin**: може змінювати аватари

### Безпека
- JWT токени з expiration
- Bcrypt хешування паролів
- Rate limiting на критичних ендпоінтах
- CORS підтримка

### Тестування
- Модульні тести для бізнес-логіки
- Інтеграційні тести для API
- Покриття >75%
- Автоматичні фікстури

## Команди Makefile

```bash
make install         # Встановити залежності
make test           # Запустити тести
make test-coverage  # Тести з покриттям
make docs           # Генерувати документацію
make docs-clean     # Очистити документацію
make clean          # Очистити тимчасові файли
make docker-up      # Запустити в Docker
make docker-down    # Зупинити Docker
make run-local      # Запустити локально
```

## Розгортання

### Хмарні сервіси
Додаток готовий для розгортання на:
- Heroku
- Railway
- Render
- DigitalOcean App Platform
- AWS/GCP/Azure

### Змінні середовища
Переконайтеся, що всі змінні з `.env` налаштовані у вашому хмарному сервісі.

## Ліцензія

MIT License