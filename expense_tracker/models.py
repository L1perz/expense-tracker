"""Сущности предметной области и проверка их значений."""

from datetime import date
from decimal import Decimal, InvalidOperation


def parse_money(text: str) -> int:
    """Преобразовать рубли в копейки без округления."""
    try:
        amount = Decimal(text.strip().replace(",", "."))
    except InvalidOperation as error:
        raise ValueError("Введите сумму числом.") from error
    if not amount.is_finite() or amount < 0:
        raise ValueError("Сумма должна быть конечной и неотрицательной.")
    if amount > Decimal("999999999999.99"):
        raise ValueError("Слишком большая сумма.")
    cents = amount * 100
    if cents != cents.to_integral_value():
        raise ValueError("Укажите сумму с точностью до копейки.")
    return int(cents)


def format_money(cents: int) -> str:
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}{cents // 100}.{cents % 100:02d} руб."


def validate_cents(value: int) -> None:
    if type(value) is not int or value <= 0:
        raise ValueError("Сумма в копейках должна быть положительным целым числом.")


def validate_month(month: str) -> None:
    try:
        parsed = date.fromisoformat(month + "-01")
    except (ValueError, TypeError) as error:
        raise ValueError("Месяц должен иметь формат ГГГГ-ММ.") from error
    if parsed.isoformat()[:7] != month:
        raise ValueError("Месяц должен иметь формат ГГГГ-ММ.")


class Transaction:
    """Базовая операция с доступными только для чтения свойствами."""

    def __init__(self, identifier: int, amount: int, operation_date: date,
                 description: str) -> None:
        if type(identifier) is not int or identifier <= 0:
            raise ValueError("ID должен быть положительным целым числом.")
        validate_cents(amount)
        if type(operation_date) is not date:
            raise ValueError("Некорректная дата операции.")
        if not isinstance(description, str) or not description.strip():
            raise ValueError("Описание не должно быть пустым.")
        self.__id = identifier
        self.__amount = amount
        self.__date = operation_date
        self.__description = description.strip()

    @property
    def id(self) -> int:
        return self.__id

    @property
    def amount(self) -> int:
        return self.__amount

    @property
    def operation_date(self) -> date:
        return self.__date

    @property
    def description(self) -> str:
        return self.__description

    def summary(self) -> str:
        return f"{self.operation_date} | {format_money(self.amount)}"


class Expense(Transaction):
    """Расход наследует поля операции и добавляет категорию."""

    def __init__(self, identifier: int, amount: int, operation_date: date,
                 description: str, category: str) -> None:
        super().__init__(identifier, amount, operation_date, description)
        if not isinstance(category, str) or not category.strip():
            raise ValueError("Категория не должна быть пустой.")
        self.__category = category.strip()

    @property
    def category(self) -> str:
        return self.__category

    def summary(self) -> str:
        """Переопределение метода базового класса (полиморфизм)."""
        return (f"#{self.id} | {super().summary()} | "
                f"{self.category} | {self.description}")

    def to_dict(self) -> dict:
        return {"id": self.id, "amount": self.amount,
                "date": self.operation_date.isoformat(),
                "description": self.description, "category": self.category}

    @classmethod
    def from_dict(cls, record: dict) -> "Expense":
        return cls(record["id"], record["amount"],
                   date.fromisoformat(record["date"]),
                   record["description"], record["category"])


class Budget:
    """Лимит расходов на конкретный месяц."""

    def __init__(self, month: str, limit: int) -> None:
        validate_month(month)
        validate_cents(limit)
        self.__month = month
        self.__limit = limit

    @property
    def month(self) -> str:
        return self.__month

    @property
    def limit(self) -> int:
        return self.__limit

    def remaining(self, spent: int) -> int:
        return self.limit - spent

    def status(self, spent: int) -> str:
        remaining = self.remaining(spent)
        if remaining > 0:
            return "Расходы в пределах бюджета."
        if remaining == 0:
            return "Бюджет израсходован полностью."
        return "Бюджет превышен!"
