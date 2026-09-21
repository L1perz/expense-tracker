"""Консольное меню и диалог с пользователем."""

from datetime import date
from pathlib import Path

from .models import format_money, parse_money, validate_month
from .service import ExpenseTracker
from .storage import JsonStorage


def read_month() -> str:
    month = input("Месяц ГГГГ-ММ (Enter - текущий): ").strip()
    month = month or date.today().isoformat()[:7]
    validate_month(month)
    return month


def read_expense() -> tuple[int, date, str, str]:
    amount = parse_money(input("Сумма в рублях: "))
    text = input("Дата ГГГГ-ММ-ДД (Enter - сегодня): ").strip()
    operation_date = date.fromisoformat(text) if text else date.today()
    category = input("Категория: ").strip()
    description = input("Описание: ").strip()
    return amount, operation_date, description, category


def show_report(tracker: ExpenseTracker, month: str) -> None:
    spent = tracker.total(month)
    print(f"\nОтчет за {month}. Всего расходов: {format_money(spent)}")
    for category, total in sorted(tracker.by_category(month).items()):
        print(f"  {category}: {format_money(total)}")
    budget = tracker.get_budget(month)
    if budget is None:
        print("Бюджет на этот месяц не задан.")
    else:
        print(f"Лимит: {format_money(budget.limit)}")
        print(f"Остаток: {format_money(budget.remaining(spent))}")
        print(budget.status(spent))


def run(path: Path) -> None:
    storage = JsonStorage(path)
    try:
        tracker = storage.load()
    except (OSError, ValueError) as error:
        print(f"Не удалось загрузить данные: {error}")
        print("Исходный файл сохранен. Исправьте его или восстановите копию.")
        return
    print("Система учета расходов | Тема №14 | ПР1–ПР3")
    print(f"Данные: {path}")
    while True:
        print("\n1. Добавить расход\n2. Список и фильтрация расходов")
        print("3. Изменить расход\n4. Удалить расход\n5. Задать бюджет")
        print("6. Отчет за месяц\n0. Выход")
        try:
            choice = input("Выберите действие: ").strip()
            if choice == "0":
                print("Работа завершена.")
                return
            # При ошибке записи исходное состояние в памяти не меняется.
            candidate = ExpenseTracker.from_dict(tracker.to_dict())
            if choice == "1":
                expense = candidate.add(*read_expense())
                message = f"Добавлен расход #{expense.id}."
            elif choice == "2":
                month = input("Месяц ГГГГ-ММ (Enter - все): ").strip()
                category = input("Категория (Enter - все): ").strip()
                expenses = tracker.list_expenses(month, category)
                for expense in expenses:
                    print(expense.summary())
                if not expenses:
                    print("Расходов не найдено.")
                continue
            elif choice == "3":
                identifier = int(input("ID расхода для изменения: "))
                candidate.update(identifier, *read_expense())
                message = "Расход изменен."
            elif choice == "4":
                identifier = int(input("ID расхода для удаления: "))
                if input("Удалить? Введите да: ").strip().casefold() != "да":
                    print("Удаление отменено.")
                    continue
                candidate.delete(identifier)
                message = "Расход удален."
            elif choice == "5":
                month = read_month()
                candidate.set_budget(month, parse_money(input("Лимит в рублях: ")))
                message = "Бюджет сохранен."
            elif choice == "6":
                show_report(tracker, read_month())
                continue
            else:
                print("Выберите пункт от 0 до 6.")
                continue
            storage.save(candidate)
            tracker = candidate
            print(message)
        except ValueError as error:
            print(f"Ошибка ввода: {error}")
        except OSError as error:
            print(f"Изменения не сохранены: {error}")
        except (EOFError, KeyboardInterrupt):
            print("\nВвод прерван. Ранее сохраненные данные остаются в файле.")
            return
