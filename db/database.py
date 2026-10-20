"""Подключения SQLite с именованными строками и внешними ключами."""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = Path(os.environ.get(
    "EXPENSE_DB_PATH", BASE_DIR / "data/expenses.sqlite"))


class DatabaseNotReady(Exception):
    """База отсутствует или ещё не содержит схему проекта."""


@contextmanager
def connection(path: Path = DEFAULT_DB_PATH, readonly: bool = True):
    """Закрыть соединение даже при исключении; не создавать БД при чтении."""
    path = Path(path).resolve()
    if readonly and not path.is_file():
        raise DatabaseNotReady("Сначала выполните python -m db.import_json.")
    if not readonly:
        path.parent.mkdir(parents=True, exist_ok=True)
    uri = path.as_uri() + ("?mode=ro" if readonly else "?mode=rwc")
    conn = sqlite3.connect(uri, uri=True, timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        with conn:
            yield conn
    finally:
        conn.close()
