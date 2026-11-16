import io
from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from django.db.models.deletion import ProtectedError
from django.test import Client
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from PIL import Image

from operations.forms import OperationForm
from accounts.models import Account
from categories.models import Category
from operations.models import Operation
from users.models import User
from ledger.queries import operations, statistics

pytestmark = pytest.mark.django_db


@pytest.fixture
def wallet():
    user = User.objects.create(name="Тест")
    account = Account.objects.create(user=user, name="Карта", balance=100_000)
    category = Category.objects.create(name="Еда")
    return user, account, category


def expense(wallet, **kwargs):
    user, account, category = wallet
    return Operation.objects.create(
        user=user,
        account=account,
        category=category,
        amount=kwargs.pop("amount", 25_000),
        description="Покупка",
        **kwargs,
    )


def test_create_edit_cancel_and_repeat(wallet):
    op = expense(wallet)
    account = wallet[1]
    account.refresh_from_db()
    assert account.balance == 75_000
    op.amount = 30_000
    op.save()
    account.refresh_from_db()
    assert account.balance == 70_000
    op.save()
    account.refresh_from_db()
    assert account.balance == 70_000
    op.cancel()
    op.cancel()
    account.refresh_from_db()
    assert account.balance == 100_000
    assert Operation.objects.cancelled().count() == 1


def test_move_between_accounts(wallet):
    op = expense(wallet)
    second = Account.objects.create(user=wallet[0], name="Наличные", balance=50_000)
    op.account = second
    op.save()
    wallet[1].refresh_from_db()
    second.refresh_from_db()
    assert wallet[1].balance == 100_000
    assert second.balance == 25_000


def test_insufficient_funds_rolls_back_edit(wallet):
    op = expense(wallet)
    op.amount = 200_000
    with pytest.raises(ValidationError):
        op.save()
    op.refresh_from_db()
    wallet[1].refresh_from_db()
    assert op.amount == 25_000
    assert wallet[1].balance == 75_000


def test_foreign_account_and_future_paid_date(wallet):
    another = User.objects.create(name="Другой")
    foreign = Account.objects.create(user=another, name="Карта", balance=100_000)
    with pytest.raises(ValidationError):
        expense((wallet[0], foreign, wallet[2]))
    with pytest.raises(ValidationError):
        expense(wallet, date=timezone.localdate() + timedelta(days=1))
    assert Operation.objects.count() == 0


def test_pending_does_not_spend_and_completed_does(wallet):
    op = expense(wallet, status=Operation.Status.PENDING)
    wallet[1].refresh_from_db()
    assert wallet[1].balance == 100_000
    op.status = Operation.Status.COMPLETED
    op.save()
    wallet[1].refresh_from_db()
    assert wallet[1].balance == 75_000


def test_protection_delete_and_stale_status(wallet):
    op = expense(wallet)
    with pytest.raises(ProtectedError):
        wallet[0].delete()
    with pytest.raises(ValidationError):
        op.delete()
    op.cancel()
    stale = Operation.objects.get(pk=op.pk)
    op.status = Operation.Status.COMPLETED
    op.save()
    with pytest.raises(ValidationError):
        stale.delete()
    op.cancel()
    op.delete()
    assert Operation.objects.count() == 0


def test_bulk_update_cannot_bypass_balance(wallet):
    op = expense(wallet)
    with pytest.raises(ValidationError):
        Operation.objects.filter(pk=op.pk).update(amount=100)
    with pytest.raises(ValidationError):
        Operation.objects.all().delete()


def test_cannot_move_account_to_another_owner(wallet):
    expense(wallet)
    wallet[1].user = User.objects.create(name="Другой")
    with pytest.raises(ValidationError):
        wallet[1].save()


def test_generated_field_and_slug(wallet):
    assert wallet[1].get_absolute_url().startswith("/accounts/by-name/")
    account = Account.objects.create(user=wallet[0], name="Запас", balance=2_000_000)
    op = expense((wallet[0], account, wallet[2]), amount=1_000_000)
    op.refresh_from_db()
    assert op.is_large
    op.amount = 999_999
    op.save()
    op.refresh_from_db()
    assert not op.is_large


def test_model_form_rubles_edit_self_and_money_validation(wallet):
    op = expense(wallet)
    data = {
        "user": wallet[0].pk,
        "account": wallet[1].pk,
        "category": wallet[2].pk,
        "amount": "250,00",
        "date": timezone.localdate().isoformat(),
        "description": "Обед",
        "status": Operation.Status.COMPLETED,
    }
    form = OperationForm(data, instance=op)
    assert form.is_valid(), form.errors
    assert form.cleaned_data["amount"] == 25_000
    form.save()
    assert Operation.objects.count() == 1
    assert OperationForm(instance=op).initial["amount"] == Decimal("250.00")
    data["amount"] = "0.001"
    assert not OperationForm(data).is_valid()
    data["amount"] = "NaN"
    assert not OperationForm(data).is_valid()


def test_category_names_are_unique_in_cyrillic(wallet):
    with pytest.raises(ValidationError):
        Category.objects.create(name="  ЕДА  ")


def test_related_objects_are_loaded_in_one_query(wallet):
    expense(wallet)
    with CaptureQueriesContext(connection) as queries:
        for op in operations():
            str(op.account), str(op.user), str(op.category)
    assert len(queries) == 1


def test_status_aware_statistics_include_empty_groups(wallet):
    expense(wallet)
    expense(wallet, status=Operation.Status.PENDING)
    op = expense(wallet)
    op.cancel()
    User.objects.create(name="Без расходов")
    result = statistics()
    assert result["summary"]["total"] == 25_000
    assert result["statuses"] == {"completed": 1, "pending": 1, "cancelled": 1}
    assert (
        next(user for user in result["users"] if user.name == "Без расходов").total == 0
    )


def test_import_is_once_and_does_not_debit(db):
    call_command("import_legacy", stdout=io.StringIO())
    account = Account.objects.get(pk=1)
    assert account.balance == 4_265_800
    assert Operation.objects.count() == 9
    with pytest.raises(CommandError):
        call_command("import_legacy", stdout=io.StringIO())
    account.refresh_from_db()
    assert account.balance == 4_265_800


def test_import_old_sqlite_and_preserve_source(tmp_path):
    from db.database import BASE_DIR
    from db.import_json import import_json

    source = tmp_path / "source.sqlite"
    import_json(BASE_DIR / "data", source)
    before = source.read_bytes()
    call_command("import_legacy", database_source=source, stdout=io.StringIO())
    assert source.read_bytes() == before
    assert Account.objects.get(pk=1).balance == 4_265_800


def test_import_failure_is_atomic(tmp_path):
    import json
    from db.database import BASE_DIR
    from shutil import copyfile

    for name in ("users", "accounts", "categories", "operations"):
        copyfile(BASE_DIR / "data" / f"{name}.json", tmp_path / f"{name}.json")
    rows = json.loads((tmp_path / "operations.json").read_text(encoding="utf-8"))
    rows[0]["user_id"] = 9999
    (tmp_path / "operations.json").write_text(json.dumps(rows), encoding="utf-8")
    with pytest.raises(CommandError):
        call_command("import_legacy", data_dir=tmp_path, stdout=io.StringIO())
    assert not User.objects.exists()
    assert not Account.objects.exists()


def test_http_forms_cancel_post_only_and_pagination(client):
    assert client.get("/operations/new/").status_code == 200
    assert client.get("/operations/1/edit/").status_code == 200
    response = client.get("/operations/?sort=amount&status=all&page=2")
    assert response.status_code == 200
    assert b"sort=amount" in response.content
    assert response.context["page_obj"].number == 2
    assert client.get("/operations/?page=bad").status_code == 200
    assert client.get("/operations/?sort=invalid").status_code == 400
    assert client.get("/operations/1/cancel/").status_code == 405
    before = Account.objects.get(pk=1).balance
    amount = Operation.objects.get(pk=1).amount
    assert client.post("/operations/1/cancel/").status_code == 302
    assert Account.objects.get(pk=1).balance == before + amount
    assert client.post("/operations/1/cancel/").status_code == 302
    assert Account.objects.get(pk=1).balance == before + amount
    assert client.get("/operations/99999/edit/").status_code == 404


def test_create_via_form_and_http_errors(client):
    account = Account.objects.get(pk=1)
    response = client.post(
        "/operations/new/",
        {
            "user": account.user_id,
            "account": account.pk,
            "category": 1,
            "amount": "10,50",
            "date": timezone.localdate().isoformat(),
            "description": "Новый расход",
            "status": "completed",
        },
    )
    assert response.status_code == 302
    assert Operation.objects.get(description="Новый расход").amount == 1050
    assert Account.objects.get(pk=1).balance == account.balance - 1050
    assert client.post("/operations/new/", {}).status_code == 200
    assert b"errorlist" not in client.get("/operations/new/").content


def test_csrf_and_get_do_not_mutate(wallet):
    op = expense(wallet)
    client = Client(enforce_csrf_checks=True)
    assert client.post(f"/operations/{op.pk}/cancel/").status_code == 403
    assert client.get(f"/operations/{op.pk}/cancel/").status_code == 405
    assert client.get("/users/new/").status_code == 200
    assert User.objects.count() == 1


def test_admin_lists_forms_and_images(client, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    admin = get_user_model().objects.create_superuser("owner", "", "test-password")
    client.force_login(admin)
    for path in (
        "/admin/",
        "/admin/accounts/account/",
        "/admin/accounts/account/add/",
        "/admin/operations/operation/1/change/",
        "/admin/accounts/account/1/change/",
    ):
        assert client.get(path).status_code == 200, path
    output = io.BytesIO()
    Image.new("RGB", (16, 16)).save(output, "PNG")
    upload = SimpleUploadedFile("card.png", output.getvalue(), content_type="image/png")
    response = client.post(
        "/accounts/1/edit/", {"user": 1, "name": "Карта", "image": upload}
    )
    assert response.status_code == 302
    account = Account.objects.get(pk=1)
    assert account.image.storage.exists(account.image.name)
    assert account.image.url.encode() in client.get(account.get_absolute_url()).content
    bad = SimpleUploadedFile("bad.png", b"not an image", content_type="image/png")
    response = client.post(
        "/accounts/1/edit/", {"user": 1, "name": "Карта", "image": bad}
    )
    assert response.status_code == 200
    assert response.context["form"].errors["image"]
