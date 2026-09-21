"""Система учета расходов: начальный сценарий ПР1."""

from datetime import date


def read_money(prompt):
    """Прочитать сумму в рублях и вернуть целое число копеек."""
    text = input(prompt).strip().replace(",", ".")
    whole, separator, fraction = text.partition(".")
    if (
        not whole.isascii()
        or not whole.isdigit()
        or (separator and (not fraction.isascii() or not fraction.isdigit()))
        or len(fraction) > 2
    ):
        return -1
    return int(whole) * 100 + int(fraction.ljust(2, "0"))


def format_money(amount):
    """Показать сумму в копейках как рубли с двумя знаками."""
    sign = "-" if amount < 0 else ""
    amount = abs(amount)
    return f"{sign}{amount // 100}.{amount % 100:02d} руб."


def calculate_total(spent_before, expense):
    """Добавить новый расход к ранее потраченной сумме."""
    return spent_before + expense


def calculate_remaining(budget, total_spent):
    """Рассчитать остаток бюджета после расхода."""
    return budget - total_spent


def get_budget_status(remaining):
    """Определить, превышен ли бюджет."""
    if remaining > 0:
        return "Расход в пределах бюджета."
    if remaining == 0:
        return "Бюджет израсходован полностью."
    return "Внимание: бюджет превышен!"


def main():
    """Учесть один расход и вывести итог за текущий месяц."""
    print("Система учета расходов | ПР1 | Тема №14")
    print("Введите суммы в рублях, например 1500 или 1500,50.")
    budget = read_money("Бюджет на текущий месяц: ")
    spent_before = read_money("Уже потрачено в этом месяце: ")
    expense = read_money("Сумма нового расхода: ")
    category = input("Категория расхода: ").strip()
    description = input("Описание расхода: ").strip()

    if budget <= 0 or spent_before < 0 or expense <= 0:
        print("Ошибка: бюджет и расход должны быть положительными,")
        print("а предыдущие расходы - неотрицательными. Не более 2 знаков")
        print("после запятой. Исправьте данные и запустите программу снова.")
        return
    if not category or not description:
        print("Ошибка: категория и описание не должны быть пустыми.")
        return

    total_spent = calculate_total(spent_before, expense)
    remaining = calculate_remaining(budget, total_spent)
    is_over_budget = remaining < 0

    print("\nРасход учтен в текущем расчете")
    print(f"Дата: {date.today():%d.%m.%Y}")
    print(f"Категория: {category}")
    print(f"Описание: {description}")
    print(f"Сумма расхода: {format_money(expense)}")
    print(f"Всего потрачено: {format_money(total_spent)}")
    print(f"Остаток бюджета: {format_money(remaining)}")
    print(get_budget_status(remaining))
    if is_over_budget:
        print(f"Превышение: {format_money(-remaining)}")
    print("Данные не сохраняются после завершения программы.")


if __name__ == "__main__":
    main()
