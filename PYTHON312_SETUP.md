# Python 3.12 Setup Guide

## Быстрая настройка Python 3.12

### Windows

```bash
# Запустить автоматическую настройку
setup_python312.bat

# Или вручную:
py -3.12 -m venv venv312
venv312\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Linux/Mac

```bash
# Запустить автоматическую настройку
chmod +x setup_python312.sh
./setup_python312.sh

# Или вручную:
python3.12 -m venv venv312
source venv312/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Проверка установки

```bash
# Активировать окружение
# Windows:
venv312\Scripts\activate

# Linux/Mac:
source venv312/bin/activate

# Проверить версию Python
python --version  # Должно быть Python 3.12.x

# Запустить проверку setup
python check_setup.py

# Запустить production checklist
python production_checklist.py
```

## После установки

1. Активируйте виртуальное окружение
2. Запустите `python production_checklist.py` для полной проверки
3. Запустите `python app.py` для старта приложения

