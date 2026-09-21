"""Управление расходами независимо от консоли и файлов."""

from datetime import date

from .models import Budget, Expense, validate_month


class ExpenseTracker:
    def __init__(self) -> None:
        self.__expenses: list[Expense] = []
        self.__budgets: dict[str, Budget] = {}
        self.__next_id = 1

    def add(self, amount: int, operation_date: date, description: str,
            category: str) -> Expense:
        expense = Expense(self.__next_id, amount, operation_date,
                          description, category)
        self.__expenses.append(expense)
        self.__next_id += 1
        return expense

    def list_expenses(self, month: str = "", category: str = "") -> list[Expense]:
        if month:
            validate_month(month)
        return sorted(
            [expense for expense in self.__expenses
             if (not month or expense.operation_date.isoformat()[:7] == month)
             and (not category or expense.category.casefold() == category.casefold())],
            key=lambda expense: (expense.operation_date, expense.id),
        )

    def update(self, identifier: int, amount: int, operation_date: date,
               description: str, category: str) -> None:
        for index, expense in enumerate(self.__expenses):
            if expense.id == identifier:
                self.__expenses[index] = Expense(
                    identifier, amount, operation_date, description, category)
                return
        raise ValueError("Расход с таким ID не найден.")

    def delete(self, identifier: int) -> None:
        for index, expense in enumerate(self.__expenses):
            if expense.id == identifier:
                del self.__expenses[index]
                return
        raise ValueError("Расход с таким ID не найден.")

    def set_budget(self, month: str, limit: int) -> None:
        self.__budgets[month] = Budget(month, limit)

    def get_budget(self, month: str) -> Budget | None:
        validate_month(month)
        return self.__budgets.get(month)

    def total(self, month: str) -> int:
        return sum(expense.amount for expense in self.list_expenses(month))

    def by_category(self, month: str) -> dict[str, int]:
        result: dict[str, int] = {}
        for expense in self.list_expenses(month):
            category = expense.category.casefold()
            result[category] = result.get(category, 0) + expense.amount
        return result

    def to_dict(self) -> dict:
        return {"version": 1, "next_id": self.__next_id,
                "expenses": [expense.to_dict() for expense in self.__expenses],
                "budgets": {month: budget.limit
                            for month, budget in self.__budgets.items()}}

    @classmethod
    def from_dict(cls, data: dict) -> "ExpenseTracker":
        if not isinstance(data, dict) or type(data.get("version")) is not int:
            raise ValueError("Некорректный формат файла данных.")
        if data["version"] != 1:
            raise ValueError("Неподдерживаемая версия файла данных.")
        if not isinstance(data["expenses"], list):
            raise ValueError("Некорректный список расходов.")
        if not isinstance(data["budgets"], dict):
            raise ValueError("Некорректный список бюджетов.")
        tracker = cls()
        identifiers: set[int] = set()
        for record in data["expenses"]:
            expense = Expense.from_dict(record)
            if expense.id in identifiers:
                raise ValueError("Повторяющийся ID расхода.")
            identifiers.add(expense.id)
            tracker.__expenses.append(expense)
        for month, limit in data["budgets"].items():
            tracker.set_budget(month, limit)
        next_id = data["next_id"]
        if type(next_id) is not int or next_id <= max(identifiers, default=0):
            raise ValueError("Некорректный следующий ID.")
        tracker.__next_id = next_id
        return tracker
