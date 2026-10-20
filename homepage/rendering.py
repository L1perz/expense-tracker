"""Начальный HTML-ответ ПР5; заменяется шаблонами на ПР6."""

from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html


def page(title, content, status=200):
    return HttpResponse(format_html(
        '<!doctype html><html lang="ru"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<link rel="stylesheet" '
        'href="https://cdn.jsdelivr.net/npm/'
        'bootstrap@5.3.3/dist/css/bootstrap.min.css">'
        '<title>{}</title></head><body><main class="container py-4">'
        '<nav><a href="{}">Главная</a> · <a href="{}">Счета</a> · '
        '<a href="{}">Операции</a></nav><h1>{}</h1>{}</main></body></html>',
        title, reverse("homepage:index"), reverse("accounts:list"),
        reverse("operations:list"), title, content,
    ), status=status)
