from django.utils.html import format_html

from .rendering import page


def index(request):
    return page("Система учёта расходов", format_html(
        "<p>Вариант 14. Пользователи, счета, категории и расходные операции.</p>"))


def page_not_found(request, exception):
    return page("Страница не найдена", format_html("<p>Проверьте адрес страницы.</p>"),
                status=404)
