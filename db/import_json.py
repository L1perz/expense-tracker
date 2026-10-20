"""Перенос JSON в SQLite: python -m db.import_json [--replace]."""

import argparse
import sqlite3
from pathlib import Path

from storage import load_project

from .database import BASE_DIR, DEFAULT_DB_PATH, connection


def import_json(data_dir: Path, database_path: Path, replace: bool = False) -> dict:
    """Проверить объекты и атомарно импортировать все связанные таблицы."""
    names = ("users", "accounts", "categories", "operations")
    for name in names:
        if not (data_dir / f"{name}.json").is_file():
            raise ValueError(f"Отсутствует исходный файл {name}.json.")
    collections = load_project(data_dir)
    with connection(database_path, readonly=False) as conn:
        conn.executescript((BASE_DIR / "sql/schema.sql").read_text(encoding="utf-8"))
        populated = any(conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
                        for name in names)
        if populated and not replace:
            raise ValueError("База уже содержит данные. Для замены укажите --replace.")
        # Все удаления и вставки находятся в одной транзакции.
        conn.execute("BEGIN IMMEDIATE")
        for name in ("operations", "accounts", "categories", "users"):
            conn.execute(f"DELETE FROM {name}")
        conn.executemany("INSERT INTO users (id, name) VALUES (:id, :name)",
                         [item.to_dict() for item in collections[0]])
        conn.executemany(
            "INSERT INTO accounts (id, user_id, name, balance) "
            "VALUES (:id, :user_id, :name, :balance)",
            [item.to_dict() for item in collections[1]],
        )
        conn.executemany("INSERT INTO categories (id, name) VALUES (:id, :name)",
                         [item.to_dict() for item in collections[2]])
        conn.executemany(
            "INSERT INTO operations "
            "(id, user_id, account_id, category_id, amount, date, description) "
            "VALUES (:id, :user_id, :account_id, :category_id, :amount, "
            ":date, :description)",
            [item.to_dict() for item in collections[3]],
        )
    return dict(zip(names, (len(items) for items in collections)))


def main() -> None:
    parser = argparse.ArgumentParser(description="Импорт объектов JSON в SQLite")
    parser.add_argument("--data-dir", type=Path, default=BASE_DIR / "data")
    parser.add_argument("--database", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--replace", action="store_true", help="Заменить данные базы")
    args = parser.parse_args()
    try:
        counts = import_json(args.data_dir, args.database, args.replace)
    except (OSError, ValueError, sqlite3.Error) as error:
        parser.exit(1, f"Ошибка импорта: {error}\n")
    result = ", ".join(f"{name}: {count}" for name, count in counts.items())
    print(f"Импорт завершён: {result}")


if __name__ == "__main__":
    main()
