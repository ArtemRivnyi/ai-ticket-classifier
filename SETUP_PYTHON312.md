# Установка Python 3.12 на Windows

## Вариант 1: Использование pyenv-win (Рекомендуется)

### Установка pyenv-win

```bash
# Через Git
git clone https://github.com/pyenv-win/pyenv-win.git %USERPROFILE%\.pyenv

# Или через установщик
# Скачайте с https://github.com/pyenv-win/pyenv-win/releases
```

### Добавление в PATH

Добавьте в переменные окружения:
- `%USERPROFILE%\.pyenv\pyenv-win\bin`
- `%USERPROFILE%\.pyenv\pyenv-win\shims`

### Установка Python 3.12

```bash
pyenv install 3.12.7
pyenv local 3.12.7
python --version  # Должно показать Python 3.12.7
```

## Вариант 2: Прямая установка с python.org

1. Скачайте Python 3.12.7 с https://www.python.org/downloads/release/python-3127/
2. Установите, убедитесь что выбрали "Add Python to PATH"
3. Проверьте:
   ```bash
   python --version  # Должно показать Python 3.12.7
   ```

## Вариант 3: Использование существующего Python 3.12 (если установлен)

Если у вас уже установлен Python 3.12, но не используется по умолчанию:

```bash
# Проверьте, установлен ли Python 3.12
py -3.12 --version

# Если установлен, используйте его для создания venv
py -3.12 -m venv venv312
venv312\Scripts\activate
python --version  # Должно показать Python 3.12.x
```

## Создание виртуального окружения

После установки Python 3.12:

```bash
# Создайте новое виртуальное окружение
python -m venv venv312

# Активируйте (Git Bash)
source venv312/Scripts/activate

# Или (PowerShell/CMD)
venv312\Scripts\activate

# Проверьте версию
python --version  # Должно быть Python 3.12.x

# Установите зависимости
pip install -r requirements.txt
```

## Проверка установки

```bash
# Проверьте версию
python --version

# Запустите production checklist
python production_checklist.py

# Запустите тесты
python -m pytest tests/ -v
```

## Если Python 3.12 не найден

Если `python --version` все еще показывает 3.14:

1. **Проверьте PATH**: Убедитесь, что Python 3.12 в PATH перед Python 3.14
2. **Используйте полный путь**: 
   ```bash
   C:\Python312\python.exe -m venv venv312
   ```
3. **Используйте py launcher**:
   ```bash
   py -3.12 -m venv venv312
   ```

## Быстрая проверка

```bash
# Проверьте доступные версии Python
py --list

# Если видите 3.12, используйте:
py -3.12 -m venv venv312
venv312\Scripts\activate
```

