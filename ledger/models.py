"""Совместимые импорты моделей прежнего расположения."""

from accounts.models import Account
from categories.models import Category
from operations.models import Operation
from users.models import User

__all__ = ["Account", "Category", "Operation", "User"]
