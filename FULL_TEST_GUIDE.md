# 🧪 Полное тестирование проекта - Production Ready Checklist

## Шаг 1: Настройка Python 3.12

### Вариант A: Автоматическая настройка (Windows)

```bash
# Запустить скрипт настройки
setup_python312.bat
```

### Вариант B: Ручная настройка

```bash
# 1. Проверить наличие Python 3.12
py -3.12 --version

# 2. Создать виртуальное окружение
py -3.12 -m venv venv312

# 3. Активировать окружение
venv312\Scripts\activate

# 4. Обновить pip
python -m pip install --upgrade pip

# 5. Установить зависимости
pip install -r requirements.txt
```

### Вариант C: Если Python 3.12 не установлен

1. Скачайте Python 3.12: https://www.python.org/downloads/
2. Установите с опцией "Add Python to PATH"
3. Повторите шаги из Варианта B

## Шаг 2: Проверка окружения

```bash
# Активировать окружение
venv312\Scripts\activate

# Проверить версию
python --version  # Должно быть 3.12.x

# Базовая проверка setup
python check_setup.py
```

## Шаг 3: Полный Production Ready Checklist

```bash
# Запустить полный production checklist
python production_checklist.py
```

Этот скрипт проверит:

### ✅ 1. Python Version & Environment
- Python version >= 3.8, < 3.14

### ✅ 2. Core Dependencies
- Flask и все необходимые пакеты
- Flask-CORS, Flask-Limiter
- Flasgger (Swagger/OpenAPI)
- Pydantic для валидации
- Prometheus client
- Redis client
- Google GenerativeAI
- PyJWT
- SQLAlchemy
- Email validator

### ✅ 3. Environment Variables
- GEMINI_API_KEY установлен
- SECRET_KEY установлен (не дефолтный)
- JWT_SECRET настроен
- FLASK_ENV установлен

### ✅ 4. Application Structure
- app.py существует
- requirements.txt существует
- Dockerfile существует
- docker-compose.prod.yml существует
- .env файл существует (опционально)

### ✅ 5. Module Imports
- Flask app импортируется
- MultiProvider импортируется
- Auth middleware импортируется
- JWT auth импортируется
- Auth blueprint импортируется
- Metrics импортируется

### ✅ 6. API Endpoints
- /api/v1/health
- /api/v1/classify
- /api/v1/batch
- /api/v1/auth/register
- /api/v1/auth/usage
- /metrics

### ✅ 7. Security Features
- CORS настроен
- Rate limiting настроен
- JWT authentication доступен
- API key authentication доступен

### ✅ 8. Monitoring & Observability
- Metrics endpoint (/metrics)
- Health check endpoint (/api/v1/health)
- Prometheus client доступен

### ✅ 9. Multi-Provider Support
- MultiProvider class существует
- CircuitBreaker pattern реализован
- AI Provider может инициализироваться
- Gemini provider доступен

### ✅ 10. API Documentation
- Swagger/Flasgger установлен
- Swagger UI endpoint существует

### ✅ 11. Input Validation & Sanitization
- Pydantic models для валидации существуют
- Input sanitization функция существует

### ✅ 12. Batch Processing
- Batch classification endpoint существует

### ✅ 13. Webhook Support
- Webhook endpoint существует

### ✅ 14. Error Handling
- Error handlers зарегистрированы

## Шаг 4: Запуск приложения

```bash
# Активировать окружение (если еще не активирован)
venv312\Scripts\activate

# Запустить приложение
python app.py

# Или в production mode
gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 app:app
```

## Шаг 5: Ручное тестирование API

### Health Check (не требует авторизации)
```bash
curl http://localhost:5000/api/v1/health
```

### Swagger UI
Откройте в браузере: http://localhost:5000/api-docs

### Регистрация нового пользователя
```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "organization": "Test Org"
  }'
```

### Классификация тикета
```bash
curl -X POST http://localhost:5000/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"ticket": "I cannot connect to VPN"}'
```

### Batch классификация
```bash
curl -X POST http://localhost:5000/api/v1/batch \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "tickets": [
      "VPN not working",
      "Password reset needed",
      "Refund request"
    ]
  }'
```

## Шаг 6: Проверка Production Checklist Results

После запуска `production_checklist.py` вы получите отчет:
- ✅ PASS: Все критичные проверки пройдены
- ⚠️ WARN: Предупреждения (не критично)
- ❌ FAIL: Ошибки (нужно исправить)

**Цель:** Все проверки должны быть PASS или WARN (без FAIL)

## Troubleshooting

### Python 3.12 не найден
```bash
# Проверить установленные версии Python
py --list

# Установить Python 3.12 с python.org
```

### Пакеты не устанавливаются
```bash
# Обновить pip
python -m pip install --upgrade pip

# Установить пакеты по одному для диагностики
pip install flask
pip install flask-cors
# и т.д.
```

### Gemini provider не инициализируется
- Проверьте что GEMINI_API_KEY установлен в .env
- Проверьте интернет соединение
- Попробуйте Python 3.11 если 3.12 не работает

### Redis не подключен
- Для локальной разработки это нормально
- В production используйте Docker Compose
- Или установите Redis локально

## Финальный Checklist

- [ ] Python 3.12 установлен и активирован
- [ ] Все зависимости установлены
- [ ] .env файл настроен с ключами
- [ ] `python check_setup.py` проходит успешно
- [ ] `python production_checklist.py` проходит успешно (>95% success rate)
- [ ] Приложение запускается без ошибок
- [ ] Health endpoint отвечает
- [ ] Swagger UI открывается
- [ ] API endpoints работают
- [ ] Классификация тикетов работает

## Готово к Production! 🚀

Если все проверки пройдены - приложение готово к развертыванию в production!

