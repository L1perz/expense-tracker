"""Сквозные проверки маршрутов, данных и ошибки 404."""

import pytest
from django.contrib.staticfiles import finders
from django.db import OperationalError
from unittest.mock import patch
from ledger.models import Operation, User


@pytest.mark.parametrize(
    "path,text",
    [
        ("/", "Система учёта расходов"),
        ("/accounts/", "Основная карта"),
        ("/accounts/1/", "Основная карта"),
        ("/operations/", "Операции"),
        ("/operations/1/", "Лев"),
        ("/users/", "Анна"),
        ("/categories/", "Здоровье"),
        ("/operations/statistics/", "Статистика"),
    ],
)
def test_pages(client, path, text):
    response = client.get(path)
    assert response.status_code == 200
    assert text in response.content.decode()


@pytest.mark.parametrize(
    "path",
    [
        "/unknown/",
        "/accounts/999/",
        "/operations/999/",
        "/accounts/abc/",
        "/accounts/999999999999999999999999999/",
        "/operations/999999999999999999999999999/",
    ],
)
def test_custom_not_found(client, path):
    response = client.get(path)
    assert response.status_code == 404
    assert "Страница не найдена" in response.content.decode()


def test_static_files_and_template_dates(client):
    for asset in ("css/style.css", "js/main.js", "img/logo.svg"):
        assert finders.find(f"homepage/{asset}")
    assert "2 октября 2026" in client.get("/operations/1/").content.decode()


def test_empty_data_and_autoescaping(client, tmp_path):
    User.objects.filter(pk=1).update(name='<script>alert("x")</script>')
    content = client.get("/users/").content.decode()
    assert "&lt;script&gt;" in content
    assert '<script>alert("x")</script>' not in content
    for operation in Operation.objects.all():
        operation.cancel()
    Operation.objects.all().delete()
    assert "Операций не найдено" in client.get("/operations/").content.decode()


@pytest.mark.parametrize(
    "path",
    [
        "/operations/?month=2026-13",
        "/operations/?month=2026",
        "/operations/?user_id=999",
        "/operations/?user_id=1%20OR%201=1",
        "/operations/?category_id=999",
        "/accounts/?max_balance=NaN",
        "/accounts/?max_balance=-10",
        "/accounts/?max_balance=1e999999",
        "/operations/statistics/?month=bad",
        "/operations/statistics/?min_total=1.001",
    ],
)
def test_invalid_filters_are_client_errors(client, path):
    response = client.get(path)
    assert response.status_code == 400
    assert "Проверьте параметры" in response.content.decode()


def test_filters_affect_displayed_results(client):
    text = client.get("/operations/?month=2026-09").content.decode()
    assert "Проездной" in text
    assert "Продукты на неделю" not in text
    text = client.get("/operations/?user_id=2&category_id=3").content.decode()
    assert "Коммунальные услуги" in text
    assert "Интернет" not in text
    text = client.get("/operations/?month=2000-01").content.decode()
    assert "Операций не найдено" in text
    assert "0,00" in text
    text = client.get("/accounts/?max_balance=8000").content.decode()
    assert "Наличные" in text
    assert "Основная карта" not in text


def test_statistics_and_having_threshold(client):
    response = client.get("/operations/statistics/?month=2026-10&min_total=1000")
    assert response.status_code == 200
    text = response.content.decode()
    assert "Продукты" in text
    assert "Дом" in text
    assert "Образование" not in text


def test_missing_database_returns_setup_page(client, tmp_path):
    path = tmp_path / "absent.sqlite"
    with patch(
        "ledger.queries.accounts", side_effect=OperationalError("no such table")
    ):
        response = client.get("/")
    assert response.status_code == 503
    assert "Данные ещё не подготовлены" in response.content.decode()
    assert not path.exists()
