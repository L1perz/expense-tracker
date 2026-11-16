"""Список словарей ORM сохраняет статусы, ссылки и связанные названия."""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from accounts.models import Account
from ledger.queries import operation_rows, operations
from operations.models import Operation

pytestmark = pytest.mark.django_db


def test_values_rows_keep_status_labels_links_and_autoescaping(client):
    account = Account.objects.get(pk=1)
    for status in Operation.Status:
        Operation.objects.create(
            user=account.user,
            account=account,
            category_id=1,
            amount=100,
            description=f"Проверка <script> {status}",
            status=status,
        )
    response = client.get(
        "/operations/",
        {
            "query": "Проверка <script>",
            "status": "all",
            "sort": "amount",
        },
    )
    assert response.status_code == 200
    rows = list(response.context["operations"])
    assert len(rows) == 3
    assert {row["status"]: row["status_label"] for row in rows} == dict(
        Operation.Status.choices
    )
    html = response.content.decode()
    assert "&lt;script&gt;" in html
    assert "Проверка <script>" not in html
    assert account.get_absolute_url() in html
    for row in rows:
        assert isinstance(row, dict)
        assert reverse("operations:detail", args=[row["id"]]) in html
        assert row["account_name"] == account.name
        assert row["user_name"] == account.user.name
    for url in ("/", account.get_absolute_url()):
        assert "status--completed" in client.get(url).content.decode()


def test_projected_related_names_use_one_query(client):
    with CaptureQueriesContext(connection) as captured:
        rows = list(operation_rows(operations())[:2])
        for row in rows:
            assert row["account_name"] and row["category_name"] and row["user_name"]
    assert len(captured) == 1
    assert "LIMIT 2" in captured[0]["sql"]
    assert "created_at" not in captured[0]["sql"]
    assert "is_large" not in captured[0]["sql"]
