"""Вспомогательные функции безопасного ввода."""

from datetime import date
from decimal import Decimal, InvalidOperation


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


def money_to_cents(text: str) -> int:
    """Преобразовать рубли в копейки без ошибок float."""
    try:
        value = Decimal(text.strip().replace(",", "."))
    except InvalidOperation as error:
        raise ValueError("Введите сумму числом.") from error
    cents = value * 100
    if value <= 0 or cents != cents.to_integral_value():
        raise ValueError("Сумма должна быть положительной, до двух знаков.")
    return int(cents)


def format_money(cents: int) -> str:
    """Преобразовать копейки в строку с рублями."""
    return f"{cents // 100}.{cents % 100:02d} руб."
