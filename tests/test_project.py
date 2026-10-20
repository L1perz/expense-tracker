"""Тесты сценариев ПР2, адаптированные к объектной модели ПР3."""

from datetime import date

import pytest

from models.accounts import add_account
from models.categories import add_category
from models.operations import calculate_total, create_operation, filter_operations
from models.users import add_user
from models import Account, Category, Operation, User


def test_add_main_entities() -> None:
    users: list = []
    accounts: list = []
    categories: list = []
    user = add_user(users, "Лев")
    account = add_account(accounts, users, user.id, "Карта", 100000)
    category = add_category(categories, "Продукты")
    assert (user.id, account.balance, category.name) == (
        1, 100000, "Продукты")


def test_create_operation_changes_balance() -> None:
    users = [User(1, "Лев")]
    accounts = [Account(1, users[0], "Карта", 100000)]
    categories = [Category(1, "Продукты")]
    operations: list = []
    operation = create_operation(
        operations, users, accounts, categories, 1, 1, 1, 25050,
        date(2026, 9, 22), "Покупка продуктов")
    assert operation.amount == 25050
    assert accounts[0].balance == 74950


def test_insufficient_money_forbidden() -> None:
    users = [User(1, "Лев")]
    accounts = [Account(1, users[0], "Карта", 100)]
    categories = [Category(1, "Продукты")]
    with pytest.raises(ValueError):
        create_operation([], users, accounts, categories, 1, 1, 1, 101,
                         date(2026, 9, 22), "Покупка")


def test_filter_and_total() -> None:
    user = User(1, "Лев")
    account = Account(1, user, "Карта", 100000)
    category = Category(1, "Продукты")
    operations = [
        Operation(i, user, account, category, amount, day, "Покупка")
        for i, amount, day in [(1, 100, date(2026, 9, 1)),
                               (2, 250, date(2026, 9, 2)),
                               (3, 500, date(2026, 10, 1))]
    ]
    assert calculate_total(filter_operations(operations, "2026-09")) == 350
