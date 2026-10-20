"""Общие проверки предметной модели."""


def integer(value: int, label: str, minimum: int = 1) -> int:
    if type(value) is not int or value < minimum:
        raise ValueError(f"{label}: требуется целое число от {minimum}.")
    return value


def name_value(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Название или имя не должно быть пустым.")
    return value.strip()


def next_id(items: list) -> int:
    return max((item.id for item in items), default=0) + 1


def find_by_id(items: list, item_id: int, label: str):
    for item in items:
        if item.id == item_id:
            return item
    raise ValueError(f"{label} не найден(а).")
