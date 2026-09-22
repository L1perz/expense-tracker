"""Функции работы со счетами (функциональная модель ПР2)."""

from users import find_user


def add_account(accounts: list[dict], users: list[dict], user_id: int,
                name: str, balance: int) -> dict:
    """Создать счёт существующего пользователя."""
    find_user(users, user_id)
    name = name.strip()
    if not name:
        raise ValueError("Название счёта не должно быть пустым.")
    if balance < 0:
        raise ValueError("Баланс не может быть отрицательным.")
    account = {
        "id": max((item["id"] for item in accounts), default=0) + 1,
        "user_id": user_id,
        "name": name,
        "balance": balance,
    }
    accounts.append(account)
    return account


def find_account(accounts: list[dict], account_id: int) -> dict:
    """Найти счёт по идентификатору."""
    for account in accounts:
        if account["id"] == account_id:
            return account
    raise ValueError("Счёт не найден.")
