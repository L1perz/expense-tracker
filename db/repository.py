"""Выполнение SQL из единого файла запросов; пользовательские значения - параметры."""

import re
import sqlite3
from datetime import date

from django.conf import settings

from .database import BASE_DIR, DatabaseNotReady, connection


def load_queries() -> dict[str, str]:
    parts = re.split(r"^-- name: (\w+)\s*$", (
        BASE_DIR / "sql/queries.sql").read_text(encoding="utf-8"), flags=re.MULTILINE)
    return dict(zip(parts[1::2], parts[2::2]))


QUERIES = load_queries()


def fetch(name: str, parameters: dict | None = None) -> list[dict]:
    with connection(settings.EXPENSE_DB_PATH) as conn:
        try:
            rows = conn.execute(QUERIES[name], parameters or {}).fetchall()
        except sqlite3.OperationalError as error:
            if "no such table" in str(error):
                raise DatabaseNotReady("Схема базы ещё не создана.") from error
            raise
    return [dict(row) for row in rows]


def get_users():
    return fetch("users")


def get_categories():
    return fetch("categories")


def get_accounts(max_balance: int | None = None):
    if max_balance is not None:
        return fetch("low_balance_accounts", {"max_balance": max_balance})
    return fetch("accounts")


def get_account(account_id: int):
    if account_id > 2**63 - 1:
        return None
    rows = fetch("account", {"id": account_id})
    return rows[0] if rows else None


def dated(rows):
    for row in rows:
        row["date"] = date.fromisoformat(row["date"])
    return rows


def get_operations(month="", user_id=None, category_id=None, account_id=None, query=""):
    if not any((month, user_id, category_id, account_id, query)):
        return dated(fetch("operations"))
    return dated(fetch("filtered_operations", {
        "month": month, "user_id": user_id, "category_id": category_id,
        "account_id": account_id, "query": query,
    }))


def get_operation(operation_id: int):
    if operation_id > 2**63 - 1:
        return None
    rows = dated(fetch("operation", {"id": operation_id}))
    return rows[0] if rows else None


def get_summary(month=""):
    return {**fetch("expense_summary", {"month": month})[0],
            **fetch("balance_summary")[0]}


def get_statistics(month="", min_total=0):
    return {
        "categories": fetch("category_totals", {
            "month": month, "min_total": min_total}),
        "users": fetch("user_totals", {"month": month}),
        "months": fetch("monthly_totals"),
        "summary": get_summary(month),
    }
