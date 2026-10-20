"""Счёт, его владелец и изменение баланса."""

from utils import format_money

from .common import find_by_id, integer, name_value, next_id
from .users import User, find_user


class Account:
    def __init__(self, account_id: int, user: User, name: str, balance: int) -> None:
        self.id = integer(account_id, "ID счёта")
        self.user = user
        self.name = name_value(name)
        self.balance = integer(balance, "Баланс", 0)

    def can_spend(self, amount: int) -> bool:
        integer(amount, "Сумма")
        return amount <= self.balance

    def withdraw(self, amount: int) -> None:
        if not self.can_spend(amount):
            raise ValueError("На счёте недостаточно денег.")
        self.balance -= amount

    def __str__(self) -> str:
        return (f"{self.id}. {self.name} ({self.user.name}): "
                f"{format_money(self.balance)}")

    def to_dict(self) -> dict:
        return {"id": self.id, "user_id": self.user.id,
                "name": self.name, "balance": self.balance}


def add_account(accounts: list[Account], users: list[User], user_id: int,
                name: str, balance: int) -> Account:
    account = Account(next_id(accounts), find_user(users, user_id), name, balance)
    accounts.append(account)
    return account


def find_account(accounts: list[Account], account_id: int) -> Account:
    return find_by_id(accounts, account_id, "Счёт")
