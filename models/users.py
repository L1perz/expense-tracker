"""Пользователь и функции обработки коллекции пользователей."""

from .common import find_by_id, integer, name_value, next_id


class User:
    def __init__(self, user_id: int, name: str) -> None:
        self.id = integer(user_id, "ID пользователя")
        self.name = name_value(name)

    def __str__(self) -> str:
        return f"{self.id}. {self.name}"

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name}


def add_user(users: list[User], name: str) -> User:
    user = User(next_id(users), name)
    users.append(user)
    return user


def find_user(users: list[User], user_id: int) -> User:
    return find_by_id(users, user_id, "Пользователь")
