"""Сквозные проверки маршрутов, данных и ошибки 404."""

import pytest


@pytest.mark.parametrize("path,text", [
    ("/", "Система учёта расходов"),
    ("/accounts/", "Основная карта"),
    ("/accounts/1/", "Основная карта"),
    ("/operations/", "Продукты на неделю"),
    ("/operations/1/", "Лев"),
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
