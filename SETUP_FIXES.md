# 🔧 Исправления для Setup

## Текущий статус после установки пакетов

✅ **Установлено успешно:**
- flask-cors
- flask-limiter
- flasgger (Swagger/OpenAPI)
- redis
- pyjwt
- sqlalchemy
- Все остальные базовые пакеты

⚠️ **Предупреждения (не критично):**

### 1. google-generativeai - Python 3.14 совместимость
**Проблема:** Python 3.14 имеет проблемы с метаклассами
```
Metaclasses with custom tp_new are not supported
```

**Решение:**
- Пакет установлен, но может выдавать предупреждения
- В runtime обычно работает нормально
- Если проблемы - используйте Python 3.11 или 3.12

**Команда для проверки:**
```bash
python -c "import google.generativeai as genai; print('OK')"
```

### 2. email-validator отсутствует
**Проблема:** Нужен для Pydantic EmailStr валидации

**Решение:**
```bash
pip install email-validator
```

### 3. GEMINI_API_KEY не установлен
**Проблема:** Предупреждение, если ключ не задан

**Решение:** Создайте `.env` файл:
```env
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here
```

### 4. Redis не запущен локально
**Проблема:** Redis не доступен (нормально для разработки)

**Решение:**
- Для локальной разработки это нормально
- В production используйте Docker Compose
- Или установите Redis локально

## Финальные команды для исправления

```bash
# 1. Установить email-validator
pip install email-validator

# 2. Создать .env файл (если еще не создан)
echo "GEMINI_API_KEY=your_key_here" > .env
echo "SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')" >> .env
echo "JWT_SECRET=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')" >> .env

# 3. Повторно проверить
python check_setup.py
```

## Проверка работоспособности

После исправлений:

```bash
# 1. Проверить setup
python check_setup.py

# 2. Попробовать запустить приложение (если GEMINI_API_KEY установлен)
python app.py

# Или в отдельном терминале проверить health endpoint:
curl http://localhost:5000/api/v1/health
```

## Рекомендации по Python версии

Если есть проблемы с `google-generativeai`:
- **Рекомендуется:** Python 3.11 или 3.12
- **Избегайте:** Python 3.14 (слишком новая версия)

Проверить версию:
```bash
python --version
```

Если используете Python 3.14, рассмотрите создание виртуального окружения с Python 3.12:
```bash
# Windows (с pyenv или используя конкретный Python)
py -3.12 -m venv venv312
venv312\Scripts\activate
pip install -r requirements.txt
```

## Итоговый статус

После выполнения всех команд выше:
- ✅ Все пакеты установлены
- ✅ Приложение должно запускаться
- ⚠️ Google Generative AI может работать несмотря на предупреждения
- ⚠️ Redis нужен только для rate limiting (можно без него для тестов)

## Быстрый тест

```bash
# Запустить приложение
python app.py

# В другом терминале
curl http://localhost:5000/api/v1/health
```

Если health endpoint отвечает - всё работает! 🎉

