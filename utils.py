"""Вспомогательные функции безопасного ввода."""

from datetime import date
from decimal import Decimal, InvalidOperation
import re


def input_int(prompt: str) -> int:
    """Повторять запрос, пока пользователь не введёт целое число."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Введите целое число.")


def input_date(prompt: str) -> date:
    """Повторять запрос до ввода даты в формате ГГГГ-ММ-ДД."""
    while True:
        try:
            return date.fromisoformat(input(prompt).strip())
        except ValueError:
            print("Введите дату в формате ГГГГ-ММ-ДД.")


def money_to_cents(text: str, allow_zero: bool = False) -> int:
    """Преобразовать рубли в копейки без ошибок float."""
    try:
        value = Decimal(text.strip().replace(",", "."))
    except InvalidOperation as error:
        raise ValueError("Введите сумму числом.") from error
    if not value.is_finite():
        raise ValueError("Сумма должна быть конечным числом.")
    if value > Decimal("92233720368547758.07"):
        raise ValueError("Сумма слишком велика.")
    if value < 0 or (value == 0 and not allow_zero):
        raise ValueError("Сумма должна быть положительной.")
    if value != value.quantize(Decimal("0.01")):
        raise ValueError("Допускается до двух знаков после запятой.")
    return int(value * 100)


def format_money(cents: int) -> str:
    """Преобразовать копейки в строку с рублями."""
    sign = "-" if cents < 0 else ""
    return f"{sign}{abs(cents) // 100}.{abs(cents) % 100:02d} руб."


def validate_month(month: str) -> str:
    """Проверить полный формат ГГГГ-ММ вместо поиска по префиксу."""
    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", month):
        raise ValueError("Введите месяц в формате ГГГГ-ММ.")
    date.fromisoformat(f"{month}-01")
    return month
