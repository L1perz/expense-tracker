"""Функции работы с пользователями (функциональная модель ПР2)."""


def add_user(users: list[dict], name: str) -> dict:
    """Добавить пользователя в коллекцию."""
    name = name.strip()
    if not name:
        raise ValueError("Имя пользователя не должно быть пустым.")
    user = {"id": max((item["id"] for item in users), default=0) + 1,
            "name": name}
    users.append(user)
    return user


def find_user(users: list[dict], user_id: int) -> dict:
    """Найти пользователя по идентификатору."""
    for user in users:
        if user["id"] == user_id:
            return user
    raise ValueError("Пользователь не найден.")
