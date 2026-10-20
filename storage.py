"""Загрузка и сохранение коллекций в JSON."""

import json
from datetime import date
from pathlib import Path

from models import Account, Category, Operation, User
from models.accounts import find_account
from models.categories import find_category
from models.users import find_user


def load_data(filename: Path) -> list[dict]:
    """Загрузить список словарей; при отсутствии файла вернуть пустой список."""
    try:
        with filename.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as error:
        raise ValueError(f"Некорректный JSON в файле {filename.name}.") from error
    if not isinstance(data, list):
        raise ValueError(f"В файле {filename.name} должен находиться список.")
    if not all(isinstance(item, dict) for item in data):
        raise ValueError(f"В файле {filename.name} ожидаются объекты JSON.")
    return data


def save_data(filename: Path, data: list[dict]) -> None:
    """Сохранить список словарей в JSON через контекстный менеджер."""
    filename.parent.mkdir(parents=True, exist_ok=True)
    temporary = filename.with_suffix(".json.tmp")
    with temporary.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    temporary.replace(filename)


def load_project(directory: Path) -> tuple[list[User], list[Account],
                                           list[Category], list[Operation]]:
    """Восстановить ссылки объектов, не списывая расходы повторно."""
    try:
        users = [User(row["id"], row["name"])
                 for row in load_data(directory / "users.json")]
        accounts = [Account(row["id"], find_user(users, row["user_id"]),
                            row["name"], row["balance"])
                    for row in load_data(directory / "accounts.json")]
        categories = [Category(row["id"], row["name"])
                      for row in load_data(directory / "categories.json")]
        operations = [Operation(
            row["id"], find_user(users, row["user_id"]),
            find_account(accounts, row["account_id"]),
            find_category(categories, row["category_id"]), row["amount"],
            date.fromisoformat(row["date"]), row["description"],
        ) for row in load_data(directory / "operations.json")]
        for items in (users, accounts, categories, operations):
            if len({item.id for item in items}) != len(items):
                raise ValueError("В JSON обнаружены повторяющиеся ID.")
        names = [item.name.casefold() for item in categories]
        if len(set(names)) != len(names):
            raise ValueError("В JSON обнаружены повторяющиеся категории.")
    except (KeyError, TypeError, AttributeError) as error:
        raise ValueError("Некорректная структура данных JSON.") from error
    return users, accounts, categories, operations


def save_project(directory: Path, users: list[User], accounts: list[Account],
                 categories: list[Category], operations: list[Operation]) -> None:
    """Сериализовать объекты в совместимый с ПР2 формат JSON."""
    for name, items in (("users", users), ("accounts", accounts),
                        ("categories", categories), ("operations", operations)):
        save_data(directory / f"{name}.json", [item.to_dict() for item in items])
