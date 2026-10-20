"""Проверки денежных правил и восстановления объектов из JSON."""

from datetime import date

import pytest

from models import Account, Category, Operation, User
from models.categories import add_category
from models.operations import create_operation, filter_operations
from storage import load_project, save_data, save_project
from utils import format_money, money_to_cents


@pytest.fixture
def entities():
    user = User(1, "Лев")
    return [user], [Account(1, user, "Карта", 10000)], [Category(1, "Еда")], []


def test_json_round_trip_restores_identity(tmp_path, entities):
    users, accounts, categories, operations = entities
    create_operation(operations, users, accounts, categories,
                     1, 1, 1, 250, date(2026, 9, 1), "Обед")
    save_project(tmp_path, *entities)
    loaded_users, loaded_accounts, loaded_categories, loaded_operations = load_project(
        tmp_path)
    operation = loaded_operations[0]
    assert operation.user is loaded_users[0]
    assert operation.account is loaded_accounts[0]
    assert operation.category is loaded_categories[0]
    assert loaded_accounts[0].balance == 9750


@pytest.mark.parametrize("bad", ["NaN", "Infinity", "-Infinity", "abc", "0", "1.001"])
def test_invalid_money_is_rejected(bad):
    with pytest.raises(ValueError):
        money_to_cents(bad)


def test_money_and_zero_initial_balance():
    assert money_to_cents("12,34") == 1234
    assert money_to_cents("0", allow_zero=True) == 0
    assert format_money(-101) == "-1.01 руб."


def test_wrong_owner_does_not_change_balance(entities):
    users, accounts, categories, operations = entities
    users.append(User(2, "Анна"))
    with pytest.raises(ValueError, match="не принадлежит"):
        create_operation(operations, users, accounts, categories,
                         2, 1, 1, 100, date(2026, 9, 1), "Обед")
    assert accounts[0].balance == 10000
    assert operations == []


def test_blank_description_does_not_change_balance(entities):
    users, accounts, categories, operations = entities
    with pytest.raises(ValueError):
        create_operation(operations, users, accounts, categories,
                         1, 1, 1, 100, date(2026, 9, 1), "  ")
    assert accounts[0].balance == 10000


def test_categories_unique_ignoring_case(entities):
    with pytest.raises(ValueError):
        add_category(entities[2], " еДА ")


@pytest.mark.parametrize("month", ["2026", "2026-1", "2026-13", "0000-01"])
def test_incomplete_month_is_rejected(month):
    with pytest.raises(ValueError):
        filter_operations([], month)


@pytest.mark.parametrize("data", [[{"id": 1}], [None], {"id": 1}])
def test_malformed_json_is_rejected(tmp_path, data):
    save_data(tmp_path / "users.json", data)
    with pytest.raises(ValueError):
        load_project(tmp_path)


def test_broken_reference_and_duplicate_id_are_rejected(tmp_path, entities):
    save_project(tmp_path, *entities)
    save_data(tmp_path / "accounts.json", [
        {"id": 1, "user_id": 99, "name": "Карта", "balance": 0}])
    with pytest.raises(ValueError):
        load_project(tmp_path)
    save_data(tmp_path / "accounts.json", [])
    save_data(tmp_path / "users.json", [{"id": 1, "name": "А"}] * 2)
    with pytest.raises(ValueError, match="повторяющиеся ID"):
        load_project(tmp_path)


def test_str_and_historical_operation(entities):
    users, accounts, categories, _ = entities
    operation = Operation(1, users[0], accounts[0], categories[0],
                          20000, date(2026, 9, 1), "Исторический расход")
    assert "Исторический расход" in str(operation)
    assert accounts[0].balance == 10000
