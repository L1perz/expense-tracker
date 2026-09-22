"""Функции работы с категориями (функциональная модель ПР2)."""


def add_category(categories: list[dict], name: str) -> dict:
    """Добавить уникальную категорию расходов."""
    name = name.strip()
    if not name:
        raise ValueError("Название категории не должно быть пустым.")
    if any(item["name"].casefold() == name.casefold()
           for item in categories):
        raise ValueError("Такая категория уже существует.")
    category = {
        "id": max((item["id"] for item in categories), default=0) + 1,
        "name": name,
    }
    categories.append(category)
    return category


def find_category(categories: list[dict], category_id: int) -> dict:
    """Найти категорию по идентификатору."""
    for category in categories:
        if category["id"] == category_id:
            return category
    raise ValueError("Категория не найдена.")
