"""Категория расхода."""

from .common import find_by_id, integer, name_value, next_id


class Category:
    def __init__(self, category_id: int, name: str) -> None:
        self.id = integer(category_id, "ID категории")
        self.name = name_value(name)

    def __str__(self) -> str:
        return f"{self.id}. {self.name}"

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name}


def add_category(categories: list[Category], name: str) -> Category:
    category = Category(next_id(categories), name)
    if any(item.name.casefold() == category.name.casefold() for item in categories):
        raise ValueError("Такая категория уже существует.")
    categories.append(category)
    return category


def find_category(categories: list[Category], category_id: int) -> Category:
    return find_by_id(categories, category_id, "Категория")
