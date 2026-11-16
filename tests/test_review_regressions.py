"""Сохранение устаревших объектов, категории в админке и поиск Unicode."""

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import connection
from django.test import Client
from django.utils import timezone

from accounts.forms import AccountForm
from accounts.models import Account
from categories.models import Category
from operations.models import Operation
from users.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def wallet():
    user = User.objects.create(name="Тест")
    account = Account.objects.create(user=user, name="Карта", balance=100_000)
    category = Category.objects.create(name="Еда")
    return user, account, category


def buy(wallet):
    return Operation.objects.create(
        user=wallet[0],
        account=wallet[1],
        category=wallet[2],
        amount=25_000,
        description="Обед",
    )


@pytest.mark.parametrize("save_method", ["model", "form", "update_fields"])
def test_stale_account_edit_keeps_current_balance(wallet, save_method):
    stale = Account.objects.get(pk=wallet[1].pk)
    buy(wallet)
    if save_method == "form":
        form = AccountForm({"user": wallet[0].pk, "name": "Другое имя"}, instance=stale)
        assert form.is_valid(), form.errors
        form.save()
    else:
        stale.name = "Другое имя"
        options = {"update_fields": ["name"]} if save_method == "update_fields" else {}
        stale.save(**options)
    current = Account.objects.get(pk=stale.pk)
    assert current.balance == stale.balance == 75_000
    assert current.name == "Другое имя"


def test_account_edit_does_not_write_balance_after_validation(wallet, monkeypatch):
    account = wallet[1]
    validate = account.full_clean

    def spend_after_validation(*args, **kwargs):
        validate(*args, **kwargs)
        buy(wallet)

    monkeypatch.setattr(account, "full_clean", spend_after_validation)
    account.name = "Новое имя"
    account.save()
    assert Account.objects.get(pk=account.pk).balance == 75_000


def test_explicit_balance_save_is_rejected(wallet):
    account = wallet[1]
    account.balance = 900_000
    with pytest.raises(ValidationError):
        account.save(update_fields=["balance"])
    assert Account.objects.get(pk=account.pk).balance == 100_000


def test_stale_cancel_preserves_latest_details_and_refunds_current_account(wallet):
    operation = buy(wallet)
    stale = Operation.objects.get(pk=operation.pk)
    second = Account.objects.create(user=wallet[0], name="Наличные", balance=50_000)
    category = Category.objects.create(name="Досуг")
    operation.account = second
    operation.category = category
    operation.amount = 30_000
    operation.description = "Исправленное описание"
    operation.date = timezone.localdate() - timedelta(days=1)
    operation.save()
    stale.cancel()
    operation.refresh_from_db()
    for field in ("amount", "description", "date", "account_id", "category_id"):
        assert getattr(operation, field) == getattr(stale, field)
    assert operation.amount == 30_000
    assert operation.description == "Исправленное описание"
    assert operation.account_id == second.pk
    assert operation.category_id == category.pk
    assert operation.status == Operation.Status.CANCELLED
    assert Account.objects.get(pk=wallet[1].pk).balance == 100_000
    assert Account.objects.get(pk=second.pk).balance == 50_000
    # Второй устаревший экземпляр не должен повторно вернуть деньги.
    operation.cancel()
    stale.cancel()
    assert Account.objects.get(pk=second.pk).balance == 50_000


@pytest.fixture
def admin_client():
    client = Client()
    client.force_login(
        get_user_model().objects.create_superuser(
            "review-owner", "", "test-only-password"
        )
    )
    return client


@pytest.mark.parametrize("edit", [False, True])
def test_admin_duplicate_category_shows_field_error(wallet, admin_client, edit):
    other = Category.objects.create(name="Дом")
    path = f"{other.pk}/change/" if edit else "add/"
    response = admin_client.post(
        f"/admin/categories/category/{path}",
        {
            "name": "  ЕДА  ",
            "operations-TOTAL_FORMS": "0",
            "operations-INITIAL_FORMS": "0",
            "operations-MIN_NUM_FORMS": "0",
            "operations-MAX_NUM_FORMS": "1000",
        },
    )
    assert response.status_code == 200
    assert (
        "Такая категория уже есть."
        in (response.context["adminform"].form.errors["name"])
    )
    assert Category.objects.count() == 2
    other.refresh_from_db()
    assert other.name == "Дом"


def test_admin_category_allows_own_case_change(wallet, admin_client):
    response = admin_client.post(
        f"/admin/categories/category/{wallet[2].pk}/change/",
        {
            "name": "ЕДА",
            "operations-TOTAL_FORMS": "0",
            "operations-INITIAL_FORMS": "0",
            "operations-MIN_NUM_FORMS": "0",
            "operations-MAX_NUM_FORMS": "1000",
        },
    )
    assert response.status_code == 302
    wallet[2].refresh_from_db()
    assert wallet[2].name == "ЕДА"
    assert Category.objects.count() == 1


@pytest.mark.parametrize("query", ["оБЕД", "кАРТА", "еДА", "тЕСТ"])
def test_cyrillic_search_matches_every_field(wallet, query):
    operation = buy(wallet)
    assert list(Operation.objects.search(query)) == [operation]
    response = Client().get("/operations/", {"query": query})
    assert response.status_code == 200
    assert [row["id"] for row in response.context["operations"]] == [operation.pk]


@pytest.mark.parametrize(
    "description,query",
    [
        ("Ёлка", "ёлКА"),
        ("Straße", "STRASSE"),
        ("Скидка 10%", "10%"),
        ("Платёж_1", "ж_1"),
        ("Путь\\чека", "\\ч"),
    ],
)
def test_unicode_search_and_literal_symbols(wallet, description, query):
    operation = buy(wallet)
    operation.description = description
    operation.save()
    assert list(Operation.objects.search(query)) == [operation]


@pytest.mark.parametrize("query", ["%", "_", "\\", "' OR 1=1 --", "НЕСУЩЕСТВУЮЩИЙ"])
def test_search_does_not_treat_input_as_sql_or_wildcards(wallet, query):
    buy(wallet)
    assert not Operation.objects.search(query).exists()


def test_search_uses_current_related_names_and_keeps_filters(wallet):
    operation = buy(wallet)
    for obj, name in zip(wallet, ("Михаил", "Новая карта", "Завтраки")):
        obj.name = name
        obj.save()
        assert Operation.objects.search(name.swapcase()).get() == operation
    assert not Operation.objects.search("Тест").exists()
    assert not Operation.objects.search("Еда").exists()
    assert not Operation.objects.cancelled().search("обед").exists()


def test_unicode_search_function_is_registered_on_new_connection():
    another = connection.copy()
    try:
        with another.cursor() as cursor:
            cursor.execute("SELECT UNICODE_CASEFOLD(%s)", ["ЁЖ Straße"])
            assert cursor.fetchone() == ("ёж strasse",)
    finally:
        another.close()


@pytest.mark.parametrize(
    "model,query",
    [
        ("operation", "обед"),
        ("operation", "карта"),
        ("operation", "еда"),
        ("operation", "тест"),
        ("account", "карта"),
        ("account", "тест"),
        ("category", "еда"),
        ("user", "тест"),
    ],
)
def test_admin_search_uses_unicode_for_all_models(wallet, admin_client, model, query):
    buy(wallet)
    app = {
        "operation": "operations",
        "account": "accounts",
        "category": "categories",
        "user": "users",
    }[model]
    response = admin_client.get(
        f"/admin/{app}/{model}/",
        {"q": query},
    )
    assert response.status_code == 200
    assert response.context["cl"].queryset.count() == 1


def test_admin_search_preserves_words_phrases_and_filters(wallet, admin_client):
    operation = buy(wallet)
    operation.description = "Обед с другом"
    operation.save()
    url = "/admin/operations/operation/"
    response = admin_client.get(url, {"q": '"ОБЕД С" ДРУГОМ'})
    assert list(response.context["cl"].queryset) == [operation]
    response = admin_client.get(url, {"q": '"С ОБЕД"'})
    assert not response.context["cl"].queryset.exists()
    response = admin_client.get(url, {"q": "обед", "status__exact": "cancelled"})
    assert not response.context["cl"].queryset.exists()
