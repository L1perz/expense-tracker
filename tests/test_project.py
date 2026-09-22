"""Тесты функциональной версии ПР2."""

from datetime import date

import pytest

from accounts import add_account
from categories import add_category
from operations import calculate_total, create_operation, filter_operations
from users import add_user


def test_add_main_entities() -> None:
    users: list[dict] = []
    accounts: list[dict] = []
    categories: list[dict] = []
    user = add_user(users, "Лев")
    account = add_account(accounts, users, user["id"], "Карта", 100000)
    category = add_category(categories, "Продукты")
    assert (user["id"], account["balance"], category["name"]) == (
        1, 100000, "Продукты")


def test_create_operation_changes_balance() -> None:
    users = [{"id": 1, "name": "Лев"}]
    accounts = [{"id": 1, "user_id": 1, "name": "Карта",
                 "balance": 100000}]
    categories = [{"id": 1, "name": "Продукты"}]
    operations: list[dict] = []
    operation = create_operation(
        operations, users, accounts, categories, 1, 1, 1, 25050,
        date(2026, 9, 22), "Покупка продуктов")
    assert operation["amount"] == 25050
    assert accounts[0]["balance"] == 74950


def test_insufficient_money_forbidden() -> None:
    users = [{"id": 1, "name": "Лев"}]
    accounts = [{"id": 1, "user_id": 1, "name": "Карта",
                 "balance": 100}]
    categories = [{"id": 1, "name": "Продукты"}]
    with pytest.raises(ValueError):
        create_operation([], users, accounts, categories, 1, 1, 1, 101,
                         date(2026, 9, 22), "Покупка")


def test_filter_and_total() -> None:
    operations = [
        {"amount": 100, "date": "2026-09-01"},
        {"amount": 250, "date": "2026-09-02"},
        {"amount": 500, "date": "2026-10-01"},
    ]
    assert calculate_total(filter_operations(operations, "2026-09")) == 350
