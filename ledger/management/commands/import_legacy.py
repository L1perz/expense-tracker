"""Однократный перенос JSON или прежней SQLite в новую базу ORM."""

import sqlite3
from datetime import date
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction

from accounts.models import Account
from categories.models import Category
from operations.models import Operation
from users.models import User
from storage import load_project


class Command(BaseCommand):
    help = (
        "Импорт данных в пустую базу. Существующие записи и исходные файлы сохраняются."
    )

    def add_arguments(self, parser):
        source = parser.add_mutually_exclusive_group()
        source.add_argument("--data-dir", type=Path, default=settings.BASE_DIR / "data")
        source.add_argument("--database-source", type=Path)

    @transaction.atomic
    def handle(self, *args, **options):
        if any(
            model.objects.exists() for model in (User, Account, Category, Operation)
        ):
            raise CommandError("В базе уже есть данные. Повторный импорт запрещён.")
        try:
            if options["database_source"]:
                path = options["database_source"].resolve()
                if path == Path(settings.DATABASES["default"]["NAME"]).resolve():
                    raise CommandError(
                        "Источник и новая база должны быть разными файлами."
                    )
                conn = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
                conn.row_factory = sqlite3.Row
                try:
                    rows = {
                        name: [
                            dict(row) for row in conn.execute(f"SELECT * FROM {name}")
                        ]
                        for name in ("users", "accounts", "categories", "operations")
                    }
                finally:
                    conn.close()
            else:
                directory = options["data_dir"]
                if not all(
                    (directory / f"{name}.json").is_file()
                    for name in ("users", "accounts", "categories", "operations")
                ):
                    raise CommandError(
                        "В каталоге нужны users/accounts/categories/operations.json."
                    )
                collections = load_project(directory)
                rows = dict(
                    zip(
                        ("users", "accounts", "categories", "operations"),
                        ([item.to_dict() for item in group] for group in collections),
                    )
                )

            users = [User(id=row["id"], name=row["name"]) for row in rows["users"]]
            categories = [
                Category(id=row["id"], name=row["name"]) for row in rows["categories"]
            ]
            for obj in users + categories:
                obj.full_clean()
            if len({obj.name.casefold() for obj in categories}) != len(categories):
                raise CommandError("В источнике повторяются названия категорий.")
            User.objects.bulk_create(users)
            Category.objects.bulk_create(categories)
            for row in rows["accounts"]:
                Account(
                    id=row["id"],
                    user_id=row["user_id"],
                    name=row["name"],
                    balance=row["balance"],
                ).save()
            operations = [
                Operation(
                    id=row["id"],
                    user_id=row["user_id"],
                    account_id=row["account_id"],
                    category_id=row["category_id"],
                    amount=row["amount"],
                    date=date.fromisoformat(row["date"]),
                    description=row["description"],
                    status=Operation.Status.COMPLETED,
                )
                for row in rows["operations"]
            ]
            for operation in operations:
                operation.full_clean()
            # Остатки источника уже учитывают исторические расходы.
            # bulk_create не вызывает save() и не списывает их повторно.
            Operation.objects.bulk_create(operations)
        except (
            OSError,
            ValueError,
            KeyError,
            TypeError,
            ValidationError,
            IntegrityError,
            sqlite3.Error,
        ) as error:
            raise CommandError(f"Импорт отменён: {error}") from error
        self.stdout.write(
            "Данные перенесены: "
            + ", ".join(f"{name}: {len(items)}" for name, items in rows.items())
        )
