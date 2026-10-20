"""Сквозные проверки маршрутов, данных и ошибки 404."""

import pytest
from django.conf import settings
from django.contrib.staticfiles import finders
from django.test import override_settings

from storage import load_project, save_project


@pytest.mark.parametrize("path,text", [
    ("/", "Система учёта расходов"),
    ("/accounts/", "Основная карта"),
    ("/accounts/1/", "Основная карта"),
    ("/operations/", "Продукты на неделю"),
    ("/operations/1/", "Лев"),
    ("/users/", "Анна"),
    ("/categories/", "Здоровье"),
])
def test_pages(client, path, text):
    response = client.get(path)
    assert response.status_code == 200
    assert text in response.content.decode()


@pytest.mark.parametrize("path", [
    "/unknown/", "/accounts/999/", "/operations/999/", "/accounts/abc/",
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
    with override_settings(DATA_DIR=tmp_path):
        content = client.get("/users/").content.decode()
        assert "&lt;script&gt;" in content
        assert '<script>alert("x")</script>' not in content
    with override_settings(DATA_DIR=tmp_path / "empty"):
        assert "Операций не найдено" in client.get("/operations/").content.decode()
