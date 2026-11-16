"""Проверка обновления и отката в отдельной SQLite, вызываемая тестом."""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "expense_tracker.settings")

import django  # noqa: E402

django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from django.contrib.auth.models import Group, Permission  # noqa: E402
from django.contrib.contenttypes.models import ContentType  # noqa: E402
from django.db import connection  # noqa: E402
from django.db.migrations.executor import MigrationExecutor  # noqa: E402
from django.test import Client  # noqa: E402
from django.test.utils import override_settings  # noqa: E402


OLD = [
    ("ledger", "0002_category_name_key"),
    ("auth", "0012_alter_user_first_name_max_length"),
    ("admin", "0003_logentry_add_action_flag_choices"),
    ("sessions", "0001_initial"),
]


def snapshot():
    with connection.cursor() as cursor:
        result = {}
        for table in (
            "ledger_user",
            "ledger_category",
            "ledger_account",
            "ledger_operation",
        ):
            cursor.execute(f'SELECT * FROM "{table}" ORDER BY id')
            result[table] = cursor.fetchall()
        return result


def main():
    executor = MigrationExecutor(connection)
    latest = executor.loader.graph.leaf_nodes()
    executor.migrate(OLD)
    old = executor.loader.project_state(OLD).apps
    User = old.get_model("ledger", "User")
    Account = old.get_model("ledger", "Account")
    Category = old.get_model("ledger", "Category")
    Operation = old.get_model("ledger", "Operation")
    owner = User.objects.create(name="Лев")
    category = Category.objects.create(name="Еда", name_key="еда")
    account = Account.objects.create(
        user=owner,
        name="Карта",
        balance=123456,
        slug="saved-account",
        image="accounts/saved.png",
    )
    for status in ("pending", "completed", "cancelled"):
        Operation.objects.create(
            user=owner,
            category=category,
            account=account,
            amount=100,
            date="2026-01-01",
            description=status,
            status=status,
            created_at="2026-01-01T12:00:00Z",
        )
    auth_user = get_user_model().objects.create_user("staff", is_staff=True)
    group = Group.objects.create(name="Финансы")
    auth_user.groups.add(group)
    types = {}
    permission_ids = {}
    for model in ("user", "category", "account", "operation"):
        content_type = ContentType.objects.create(app_label="ledger", model=model)
        types[model] = content_type.pk
        permission = Permission.objects.create(
            content_type=content_type, codename=f"view_{model}", name=model
        )
        permission_ids[model] = permission.pk
        group.permissions.add(permission)
    # Проверяем также слияние прав после частичного обновления.
    duplicate = ContentType.objects.create(app_label="operations", model="operation")
    permission = Permission.objects.create(
        content_type=duplicate, codename="view_operation", name="view"
    )
    auth_user.user_permissions.add(permission)
    extra_group = Group.objects.create(name="Дополнительные права")
    extra_group.permissions.add(permission)
    log = old.get_model("admin", "LogEntry").objects.create(
        user_id=auth_user.pk,
        content_type_id=duplicate.pk,
        object_id="1",
        object_repr="Операция",
        action_flag=2,
    )
    before = snapshot()
    MigrationExecutor(connection).migrate(latest)
    assert snapshot() == before
    mapping = {
        "user": "users",
        "category": "categories",
        "account": "accounts",
        "operation": "operations",
    }
    ContentType.objects.clear_cache()
    for model, app in mapping.items():
        content_type = ContentType.objects.get(app_label=app, model=model)
        assert content_type.pk == types[model]
        assert (
            Permission.objects.get(
                content_type=content_type, codename=f"view_{model}"
            ).pk
            == permission_ids[model]
        )
        assert (
            get_user_model()
            .objects.get(pk=auth_user.pk)
            .has_perm(f"{app}.view_{model}")
        )
    assert auth_user.user_permissions.filter(pk=permission_ids["operation"]).exists()
    assert extra_group.permissions.filter(pk=permission_ids["operation"]).exists()
    assert (
        old.get_model("admin", "LogEntry").objects.get(pk=log.pk).content_type_id
        == (types["operation"])
    )
    with override_settings(ALLOWED_HOSTS=["testserver"]):
        client = Client()
        client.force_login(auth_user)
        for model, app in mapping.items():
            assert client.get(f"/admin/{app}/{model}/").status_code == 200
    MigrationExecutor(connection).migrate(OLD)
    assert snapshot() == before
    for model in mapping:
        assert ContentType.objects.get(pk=types[model]).app_label == "ledger"
    MigrationExecutor(connection).migrate(latest)
    assert snapshot() == before
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA foreign_key_check")
        assert cursor.fetchall() == []
    print(
        json.dumps(
            {
                "upgrade": "ok",
                "rollback": "ok",
                "permissions": "ok",
                "counts": {key: len(rows) for key, rows in before.items()},
            }
        )
    )


if __name__ == "__main__":
    main()
