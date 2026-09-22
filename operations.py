"""Функции работы с расходными операциями (ПР2)."""

from datetime import date

from accounts import find_account
from categories import find_category
from users import find_user


def create_operation(operations: list[dict], users: list[dict],
                     accounts: list[dict], categories: list[dict],
                     user_id: int, account_id: int, category_id: int,
                     amount: int, operation_date: date,
                     description: str) -> dict:
    """Создать расход и уменьшить баланс выбранного счёта."""
    find_user(users, user_id)
    account = find_account(accounts, account_id)
    find_category(categories, category_id)
    if account["user_id"] != user_id:
        raise ValueError("Счёт не принадлежит выбранному пользователю.")
    if amount <= 0:
        raise ValueError("Сумма расхода должна быть больше нуля.")
    if amount > account["balance"]:
        raise ValueError("На счёте недостаточно денег.")
    description = description.strip()
    if not description:
        raise ValueError("Описание не должно быть пустым.")
    operation = {
        "id": max((item["id"] for item in operations), default=0) + 1,
        "user_id": user_id,
        "account_id": account_id,
        "category_id": category_id,
        "amount": amount,
        "date": operation_date.isoformat(),
        "description": description,
    }
    account["balance"] -= amount
    operations.append(operation)
    return operation


def filter_operations(operations: list[dict], month: str) -> list[dict]:
    """Вернуть операции указанного месяца ГГГГ-ММ."""
    return [item for item in operations if item["date"].startswith(month)]


def calculate_total(operations: list[dict]) -> int:
    """Рассчитать общую сумму переданных расходов."""
    return sum(item["amount"] for item in operations)
