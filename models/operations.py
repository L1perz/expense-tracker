"""Расход связывает объекты пользователя, счёта и категории."""

from datetime import date

from utils import format_money, validate_month

from .accounts import Account, find_account
from .categories import Category, find_category
from .common import integer, name_value, next_id
from .users import User, find_user


class Operation:
    def __init__(self, operation_id: int, user: User, account: Account,
                 category: Category, amount: int, operation_date: date,
                 description: str) -> None:
        self.id = integer(operation_id, "ID операции")
        if account.user.id != user.id:
            raise ValueError("Счёт не принадлежит выбранному пользователю.")
        if type(operation_date) is not date:
            raise ValueError("Требуется дата операции.")
        self.user = user
        self.account = account
        self.category = category
        self.amount = integer(amount, "Сумма расхода")
        self.date = operation_date
        self.description = name_value(description)

    def __str__(self) -> str:
        return (f"{self.id}. {self.date}: {self.description}, "
                f"{self.category.name}, {format_money(self.amount)}")

    def to_dict(self) -> dict:
        return {"id": self.id, "user_id": self.user.id,
                "account_id": self.account.id, "category_id": self.category.id,
                "amount": self.amount, "date": self.date.isoformat(),
                "description": self.description}


def create_operation(operations: list[Operation], users: list[User],
                     accounts: list[Account], categories: list[Category],
                     user_id: int, account_id: int, category_id: int,
                     amount: int, operation_date: date,
                     description: str) -> Operation:
    operation = Operation(
        next_id(operations), find_user(users, user_id),
        find_account(accounts, account_id), find_category(categories, category_id),
        amount, operation_date, description,
    )
    operation.account.withdraw(amount)
    operations.append(operation)
    return operation


def filter_operations(operations: list[Operation], month: str) -> list[Operation]:
    validate_month(month)
    return [item for item in operations if item.date.strftime("%Y-%m") == month]


def calculate_total(operations: list[Operation]) -> int:
    return sum(item.amount for item in operations)
