"""Сквозные проверки маршрутов, данных и ошибки 404."""

import pytest
from django.conf import settings
from django.contrib.staticfiles import finders
from django.test import override_settings

from storage import load_project, save_project
from db.import_json import import_json


@pytest.mark.parametrize("path,text", [
    ("/", "Система учёта расходов"),
    ("/accounts/", "Основная карта"),
    ("/accounts/1/", "Основная карта"),
    ("/operations/", "Продукты на неделю"),
    ("/operations/1/", "Лев"),
    ("/users/", "Анна"),
    ("/categories/", "Здоровье"),
    ("/operations/statistics/", "Статистика"),
])
def test_pages(client, path, text):
    response = client.get(path)
    assert response.status_code == 200
    assert text in response.content.decode()


@pytest.mark.parametrize("path", [
    "/unknown/", "/accounts/999/", "/operations/999/", "/accounts/abc/",
    "/accounts/999999999999999999999999999/",
    "/operations/999999999999999999999999999/",
])
def test_custom_not_found(client, path):
    response = client.get(path)
    assert response.status_code == 404
    assert "Страница не найдена" in response.content.decode()


def test_static_files_and_template_dates(client):
    for asset in ("css/style.css", "js/main.js", "img/logo.svg"):
        assert finders.find(f"homepage/{asset}")
    assert "2 октября 2026" in client.get("/operations/1/").content.decode()


def test_empty_data_and_autoescaping(client, tmp_path):
    data = load_project(settings.DATA_DIR)
    data[0][0].name = '<script>alert("x")</script>'
    save_project(tmp_path, *data)
    database = tmp_path / "escaped.sqlite"
    import_json(tmp_path, database)
    with override_settings(EXPENSE_DB_PATH=database):
        content = client.get("/users/").content.decode()
        assert "&lt;script&gt;" in content
        assert '<script>alert("x")</script>' not in content
    empty = tmp_path / "empty"
    save_project(empty, [], [], [], [])
    database = tmp_path / "empty.sqlite"
    import_json(empty, database)
    with override_settings(EXPENSE_DB_PATH=database):
        assert "Операций не найдено" in client.get("/operations/").content.decode()


@pytest.mark.parametrize("path", [
    "/operations/?month=2026-13", "/operations/?month=2026",
    "/operations/?user_id=999", "/operations/?user_id=1%20OR%201=1",
    "/operations/?category_id=999", "/accounts/?max_balance=NaN",
    "/accounts/?max_balance=-10", "/accounts/?max_balance=1e999999",
    "/operations/statistics/?month=bad", "/operations/statistics/?min_total=1.001",
])
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
    assert "0.00 руб." in text
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
    with override_settings(EXPENSE_DB_PATH=path):
        response = client.get("/")
    assert response.status_code == 503
    assert "Данные ещё не подготовлены" in response.content.decode()
    assert not path.exists()
