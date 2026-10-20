"""Проверки SQL-выборок, импорта и ограничений целостности."""

import sqlite3

import pytest
from django.test import override_settings

from db import repository
from db.database import BASE_DIR, DatabaseNotReady, connection
from db.import_json import import_json
from storage import load_project, save_project


@pytest.fixture
def database(tmp_path):
    path = tmp_path / "expenses.sqlite"
    import_json(BASE_DIR / "data", path)
    with override_settings(EXPENSE_DB_PATH=path):
        yield path


def test_queries_match_known_data(database):
    assert len(repository.QUERIES) >= 10
    assert len(repository.get_users()) == 3
    assert len(repository.get_categories()) == 5
    assert len(repository.get_accounts()) == 4
    assert repository.get_accounts(800000)[0]["name"] == "Наличные"
    assert repository.get_account(1)["user_name"] == "Лев"
    assert repository.get_account(999) is None
    assert len(repository.get_operations()) == 9
    assert repository.get_operation(1)["category_name"] == "Продукты"
    assert repository.get_operation(999) is None
    assert len(repository.get_operations(month="2026-09")) == 2
    assert len(repository.get_operations(user_id=2, category_id=3)) == 1
    assert len(repository.get_operations(account_id=2)) == 2
    assert len(repository.get_operations(query="Интернет")) == 1
    assert repository.get_operations(query="' OR 1=1 --") == []
    assert repository.get_summary("2026-09")["total"] == 116000
    assert repository.get_summary("2026-09")["count"] == 2
    stats = repository.get_statistics("2026-10", 100000)
    assert {row["name"] for row in stats["categories"]} == {"Продукты", "Дом"}
    assert next(row for row in stats["users"] if row["id"] == 3)["count"] == 0
    assert len(stats["months"]) == 2


def test_all_named_queries_execute_with_parameters(database):
    parameters = {"id": 1, "month": "", "min_total": 0, "max_balance": 1000000,
                  "user_id": None, "category_id": None, "account_id": None, "query": ""}
    with connection(database) as conn:
        for sql in repository.QUERIES.values():
            assert conn.execute(sql, parameters).fetchall() is not None
        assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
        assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"


@pytest.mark.parametrize("values", [
    (99, 2, 1, 1, 100, "2026-10-20", "Чужой владелец"),
    (99, 99, 1, 1, 100, "2026-10-20", "Нет пользователя"),
    (99, 1, 1, 99, 100, "2026-10-20", "Нет категории"),
    (99, 1, 1, 1, -1, "2026-10-20", "Отрицательная сумма"),
    (99, 1, 1, 1, 100, "2026-02-30", "Неверная дата"),
    (99, 1, 1, 1, 100, "invalid", "Неверная дата"),
])
def test_database_constraints(database, values):
    with pytest.raises(sqlite3.IntegrityError):
        with connection(database, readonly=False) as conn:
            conn.execute("INSERT INTO operations VALUES (?, ?, ?, ?, ?, ?, ?)", values)
    assert len(repository.get_operations()) == 9


def test_import_protects_existing_data_and_does_not_debit(database):
    balance = repository.get_account(1)["balance"]
    with pytest.raises(ValueError, match="уже содержит"):
        import_json(BASE_DIR / "data", database)
    import_json(BASE_DIR / "data", database, replace=True)
    assert repository.get_account(1)["balance"] == balance == 4265800
    assert len(repository.get_operations()) == 9


def test_failed_replacement_keeps_existing_rows(database, tmp_path):
    data = load_project(BASE_DIR / "data")
    # Имитируем ошибку вставки уже после удаления строк в транзакции.
    save_project(tmp_path / "source", *data)
    with connection(database, readonly=False) as conn:
        conn.execute("CREATE TRIGGER reject_user BEFORE INSERT ON users "
                     "BEGIN SELECT RAISE(ABORT, 'test failure'); END")
    with pytest.raises(sqlite3.IntegrityError):
        import_json(tmp_path / "source", database, replace=True)
    assert len(repository.get_users()) == 3
    assert len(repository.get_operations()) == 9


def test_missing_source_does_not_touch_database(database, tmp_path):
    with pytest.raises(ValueError, match="исходный файл"):
        import_json(tmp_path / "missing", database, replace=True)
    assert len(repository.get_users()) == 3


def test_missing_database_is_not_created(tmp_path):
    path = tmp_path / "missing.sqlite"
    with pytest.raises(DatabaseNotReady):
        with connection(path):
            pass
    assert not path.exists()


def test_empty_aggregates_and_zero_groups(database, tmp_path):
    data = load_project(BASE_DIR / "data")
    data[3].clear()
    save_project(tmp_path / "empty", *data)
    import_json(tmp_path / "empty", database, replace=True)
    summary = repository.get_summary()
    assert summary["count"] == summary["total"] == summary["minimum"] == 0
    stats = repository.get_statistics()
    assert len(stats["categories"]) == 5
    assert all(row["count"] == row["total"] == 0 for row in stats["categories"])
