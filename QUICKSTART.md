# 🚀 Quick Start Guide

## Быстрый старт для Production

### 1. Установка зависимостей

```bash
# Клонировать репозиторий
git clone <your-repo-url>
cd ai-ticket-classifier

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
# Обязательные
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your-random-secret-key-here
JWT_SECRET=your-jwt-secret-key-here

# Опциональные (для fallback)
OPENAI_API_KEY=your_openai_key_here

# Redis (для production)
REDIS_URL=redis://redis:6379/0

# CORS (список разрешенных доменов через запятую)
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Security
FORCE_HTTPS=true

# Logging
LOG_LEVEL=INFO
FLASK_ENV=production
```

### 3. Запуск с Docker Compose (Рекомендуется)

```bash
# Запустить все сервисы (App, Redis, Prometheus, Grafana)
docker-compose -f docker-compose.prod.yml up --build -d

# Проверить статус
docker-compose -f docker-compose.prod.yml ps

# Просмотр логов
docker-compose -f docker-compose.prod.yml logs -f app
```

### 4. Запуск без Docker (для разработки)

```bash
# Убедитесь что Redis запущен
# Windows: скачайте и запустите Redis
# Linux/Mac: redis-server

# Запустить приложение
python app.py

# Или с Gunicorn (production)
gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 app:app
```

### 5. Регистрация и получение API ключа

```bash
# Регистрация нового пользователя
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "John Doe",
    "organization": "Example Inc"
  }'

# Ответ:
# {
#   "user_id": "usr_xxx",
#   "api_key": "atc_xxx",
#   "jwt_token": "eyJxxx",
#   "tier": "free",
#   "limits": {...}
# }
```

### 6. Использование API

#### Классификация одного тикета

```bash
curl -X POST http://localhost:5000/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "ticket": "I cannot connect to VPN"
  }'
```

#### Batch классификация

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

#### Использование JWT токена

```bash
# Получить JWT токен из API ключа
curl -X POST http://localhost:5000/api/v1/auth/jwt/login \
  -H "X-API-Key: YOUR_API_KEY"

# Использовать JWT токен
curl -X POST http://localhost:5000/api/v1/classify \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"ticket": "Cannot access my account"}'
```

### 7. Доступ к документации и мониторингу

- **Swagger UI**: http://localhost:5000/api-docs
- **Health Check**: http://localhost:5000/api/v1/health
- **Prometheus Metrics**: http://localhost:5000/metrics
- **Grafana Dashboard**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

### 8. Проверка работоспособности

```bash
# Health check
curl http://localhost:5000/api/v1/health

# Должен вернуть:
# {
#   "status": "healthy",
#   "version": "2.0.0",
#   "timestamp": "2025-01-15T...",
#   "environment": "production",
#   "provider_status": {
#     "gemini": "available",
#     "openai": "unavailable"
#   }
# }
```

## Структура проекта

```
ai-ticket-classifier/
├── app.py                 # Главный файл приложения
├── api/                   # API endpoints
│   └── auth.py           # Authentication endpoints
├── providers/            # AI провайдеры
│   ├── multi_provider.py # Multi-provider с circuit breaker
│   └── gemini_provider.py
├── middleware/           # Middleware
│   └── auth.py          # API key authentication
├── security/            # Security модули
│   └── jwt_auth.py     # JWT authentication
├── database/           # Database models
│   └── models.py
├── monitoring/         # Monitoring
│   └── metrics.py
├── docker-compose.prod.yml  # Production Docker setup
└── requirements.txt    # Dependencies
```

## Production Checklist

- [ ] Измените `SECRET_KEY` и `JWT_SECRET` на случайные значения
- [ ] Настройте `CORS_ORIGINS` для вашего домена
- [ ] Установите `FORCE_HTTPS=true` в production
- [ ] Настройте PostgreSQL для persistence (опционально)
- [ ] Настройте мониторинг в Grafana
- [ ] Настройте резервное копирование БД
- [ ] Настройте SSL/TLS сертификаты
- [ ] Настройте логирование в централизованную систему
- [ ] Протестируйте failover между провайдерами
- [ ] Настройте rate limits согласно вашим tier'ам

## Troubleshooting

### Ошибка подключения к Redis
```bash
# Проверьте что Redis запущен
docker ps | grep redis
# Или
redis-cli ping
```

### Ошибка инициализации провайдера
- Проверьте что `GEMINI_API_KEY` установлен
- Проверьте интернет соединение
- Проверьте логи: `docker-compose logs app`

### Rate limit exceeded
- Увеличьте tier через админ-панель
- Или используйте более высокий tier при регистрации

## Поддержка

Для вопросов и поддержки:
- GitHub Issues: [ваш репозиторий]/issues
- Email: support@example.com

