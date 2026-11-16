"""Консоль использует ту же базу и те же правила списания, что и сайт."""

from datetime import date

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import DatabaseError

from accounts.models import Account
from categories.models import Category
from operations.models import Operation
from users.models import User
from ledger.queries import period, summary
from utils import format_money, money_to_cents, validate_month


def main():
    while True:
        print("\nСистема учёта расходов")
        print("1. Пользователь  2. Счёт  3. Категория  4. Расход")
        print("5. Список  6. Отчёт за месяц  7. Отменить расход  0. Выход")
        try:
            choice = input("Действие: ").strip()
            if choice == "0":
                return
            if choice == "1":
                obj = User(name=input("Имя: ").strip())
                obj.full_clean()
                obj.save()
            elif choice == "2":
                Account.objects.create(
                    user=User.objects.get(pk=int(input("ID пользователя: "))),
                    name=input("Название: ").strip(),
                    balance=money_to_cents(
                        input("Начальный баланс: "), allow_zero=True
                    ),
                )
            elif choice == "3":
                obj = Category(name=input("Категория: ").strip())
                obj.full_clean()
                obj.save()
            elif choice == "4":
                Operation.objects.create(
                    user=User.objects.get(pk=int(input("ID пользователя: "))),
                    account=Account.objects.get(pk=int(input("ID счёта: "))),
                    category=Category.objects.get(pk=int(input("ID категории: "))),
                    amount=money_to_cents(input("Сумма, руб.: ")),
                    date=date.fromisoformat(
                        input("Дата ГГГГ-ММ-ДД: ") or date.today().isoformat()
                    ),
                    description=input("Описание: ").strip(),
                )
            elif choice == "5":
                for title, items in (
                    ("Пользователи", User.objects.all()),
                    ("Счета", Account.objects.select_related("user")),
                    ("Категории", Category.objects.all()),
                    ("Операции", Operation.objects.with_details()),
                ):
                    print(title)
                    for item in items:
                        print(item.pk, item)
            elif choice == "6":
                month = input("Месяц ГГГГ-ММ: ").strip()
                validate_month(month)
                print("Расходы:", format_money(summary(month)["total"]))
                print("Операций:", period(Operation.objects.completed(), month).count())
            elif choice == "7":
                Operation.objects.get(pk=int(input("ID операции: "))).cancel()
            else:
                print("Выберите пункт от 0 до 7.")
        except (ValueError, ValidationError, ObjectDoesNotExist) as error:
            print(f"Ошибка ввода: {error}")
        except DatabaseError:
            print("Не удалось изменить базу. Проверьте миграции и повторите действие.")
        except (EOFError, KeyboardInterrupt):
            print("\nРабота завершена.")
            return
