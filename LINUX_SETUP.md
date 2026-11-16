# Установка на Linux

## Пакеты

Arch Linux:

```bash
sudo pacman -Syu --needed git python python-pip
```

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install git python3 python3-venv python3-pip
```

Нужны Python 3.11–3.14 и SQLite 3.37+:

```bash
python3 --version
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
```

## Первая установка

```bash
git clone https://github.com/L1perz/expense-tracker.git
cd expense-tracker
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py import_legacy
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver
```

Последние две команды: создать собственный вход в админку и запустить сервер.
Импорт нужен один раз, если нужны демонстрационные данные.
Открыть <http://127.0.0.1:8000/>; админка — <http://127.0.0.1:8000/admin/>.
Остановка — Ctrl+C. Окружение Windows на Linux не копируется, а создаётся заново.

## Повторный запуск

```bash
cd ~/expense-tracker
.venv/bin/python manage.py runserver
```

Консоль с той же базой:

```bash
.venv/bin/python main.py
```

## Обновление

Сначала проверить локальные изменения и сохранить копию данных.
Если `git status` показывает изменённые файлы, их нужно сохранить отдельным коммитом
или в `git stash`, а не удалять. Не применять `git reset --hard` для обновления.

```bash
git status
git pull --ff-only
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py check
```

Старая база `data/expenses.sqlite` остаётся отдельным источником. В пустую
`data/ledger.sqlite3` её можно перенести после миграций:

```bash
.venv/bin/python manage.py import_legacy --database-source data/expenses.sqlite
```

Не запускать повторный импорт демонстрационных данных при обычном обновлении.

## Частые ошибки

- Нет `manage.py`: открыта старая консольная версия или другая папка.
  Проверить `pwd`, `git log -1`, `git status` и наличие актуальной ветки.
- `No module named django`: выполнить установку через `.venv/bin/python -m pip`.
- `No such table`: выполнить `.venv/bin/python manage.py migrate` для выбранной базы.
- `База уже содержит данные`: повторный импорт не нужен; данные сохранены.
- Порт занят: `.venv/bin/python manage.py runserver 127.0.0.1:8001`.
- Пустые списки: добавить данные через формы либо один раз вызвать `import_legacy`.
- Изображения не открываются: при локальной работе нужен `DEBUG=True` и файл
  в `media/`; SQLite хранит только относительный путь к изображению.

Проверки:

```bash
.venv/bin/python manage.py makemigrations --check --dry-run
.venv/bin/python -m pytest -q
.venv/bin/python -m flake8
```
