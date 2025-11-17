# 🔍 Команда для проверки установки

## Быстрая проверка

Запустите эту команду для полной проверки:

```bash
python check_setup.py
```

## Что проверяет скрипт:

1. ✅ **Версия Python** (>= 3.8)
2. ✅ **Установленные пакеты**:
   - flask
   - flask-cors
   - flask-limiter
   - flasgger (Swagger/OpenAPI)
   - pydantic
   - prometheus-client
   - redis
   - google-generativeai
   - pyjwt (JWT)
   - sqlalchemy
   - requests
   - python-dotenv

3. ✅ **Переменные окружения**:
   - GEMINI_API_KEY (опционально для проверки)
   - SECRET_KEY

4. ✅ **Импорты модулей**:
   - app.py
   - providers.multi_provider
   - middleware.auth
   - security.jwt_auth
   - api.auth
   - monitoring.metrics

5. ✅ **Flask приложение**:
   - Инициализация приложения
   - SECRET_KEY настроен

6. ✅ **Redis** (опционально)

7. ✅ **Swagger/OpenAPI** конфигурация

8. ✅ **Routes** (маршруты API)

## Пример вывода:

### ✅ Если все установлено:
```
============================================================
AI Ticket Classifier - Setup Verification
============================================================

[1/8] Checking Python version...
[OK] Python version >= 3.8

[2/8] Checking required packages...
[OK] Package: flask
[OK] Package: flask-cors
...

============================================================
SUMMARY
============================================================
Successful checks: 25
Warnings: 2
Errors: 0

All checks passed! Setup is complete.
```

### ❌ Если есть ошибки:
```
ERRORS FOUND:
   - Package: flask_cors: No module named 'flask_cors'
   - Package: flask_limiter: No module named 'flask_limiter'

MISSING PACKAGES DETECTED:
   Missing: flask-cors, flask-limiter, flasgger, redis, pyjwt, sqlalchemy

TO FIX, RUN THIS COMMAND:
   pip install flask-cors flask-limiter flasgger redis pyjwt sqlalchemy

OR REINSTALL ALL REQUIREMENTS:
   pip install -r requirements.txt
```

## Команда для исправления

Если скрипт показал ошибки, выполните:

```bash
pip install -r requirements.txt
```

Или установите недостающие пакеты вручную:

```bash
pip install flask-cors flask-limiter flasgger redis pyjwt sqlalchemy
```

## После проверки

1. Если все проверки прошли ✅:
   - Создайте `.env` файл с `GEMINI_API_KEY`
   - Запустите: `python app.py`

2. Если есть ошибки ❌:
   - Выполните команду из вывода скрипта
   - Повторно запустите `python check_setup.py`

## Альтернативные способы проверки

### Windows (Batch):
```cmd
verify_setup.bat
```

### Linux/Mac (Bash):
```bash
chmod +x verify_setup.sh
./verify_setup.sh
```

## Что делать с предупреждениями

- **GEMINI_API_KEY not set** - это нормально, можно установить позже в `.env`
- **Redis not running** - нормально для локальной разработки, в production нужен Redis
- **Flask app warnings** - проверьте, что все зависимости установлены

---

**Полная команда для проверки:**
```bash
python check_setup.py
```

Скопируйте весь вывод и отправьте для анализа, если есть проблемы!

