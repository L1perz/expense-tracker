"""Консольная система учёта расходов: объекты ПР3 и JSON."""

from pathlib import Path

from models.accounts import add_account
from models.categories import add_category
from models.operations import calculate_total, create_operation, filter_operations
from storage import load_project, save_project
from models.users import add_user
from utils import format_money, input_date, input_int, money_to_cents

DATA_DIR = Path(__file__).parent / "data"


def show_items(title: str, items: list) -> None:
    """Вывести коллекцию объектов через их строковое представление."""
    print(f"\n{title}")
    if not items:
        print("Список пуст.")
    for item in items:
        print(item)


def main() -> None:
    """Загрузить данные и запустить цикл меню."""
    try:
        users, accounts, categories, operations = load_project(DATA_DIR)
    except (OSError, ValueError) as error:
        print(f"Ошибка загрузки: {error}")
        return

    while True:
        print("\n=== Система учёта расходов ===")
        print("1. Добавить пользователя")
        print("2. Добавить счёт")
        print("3. Добавить категорию")
        print("4. Записать расход")
        print("5. Показать данные")
        print("6. Отчёт за месяц")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()
        try:
            if choice == "0":
                return
            if choice == "1":
                add_user(users, input("Имя: "))
            elif choice == "2":
                add_account(accounts, users, input_int("ID пользователя: "),
                            input("Название счёта: "),
                            money_to_cents(input("Начальный баланс: "),
                                           allow_zero=True))
            elif choice == "3":
                add_category(categories, input("Название категории: "))
            elif choice == "4":
                create_operation(
                    operations, users, accounts, categories,
                    input_int("ID пользователя: "),
                    input_int("ID счёта: "),
                    input_int("ID категории: "),
                    money_to_cents(input("Сумма: ")),
                    input_date("Дата ГГГГ-ММ-ДД: "),
                    input("Описание: "),
                )
            elif choice == "5":
                show_items("Пользователи", users)
                show_items("Счета", accounts)
                show_items("Категории", categories)
                show_items("Операции", operations)
                continue
            elif choice == "6":
                month = input("Месяц ГГГГ-ММ: ").strip()
                total = calculate_total(filter_operations(operations, month))
                print(f"Расходы за {month}: {format_money(total)}")
                continue
            else:
                print("Неизвестный пункт меню.")
                continue
            save_project(DATA_DIR, users, accounts, categories, operations)
            print("Данные сохранены.")
        except (OSError, ValueError) as error:
            print(f"Ошибка: {error}")


if __name__ == "__main__":
    main()
