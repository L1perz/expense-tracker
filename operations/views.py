from django.conf import settings
from django.http import Http404
from django.urls import reverse
from django.utils.html import format_html, format_html_join

from homepage.rendering import page
from storage import load_project


def operation_list(request):
    _, _, _, operations = load_project(settings.DATA_DIR)
    content = format_html_join("", '<p><a href="{}">{}</a></p>', (
        (reverse("operations:detail", args=[operation.id]), str(operation))
        for operation in operations))
    return page("Операции", content or format_html("<p>Список пуст.</p>"))


def operation_detail(request, operation_id):
    _, _, _, operations = load_project(settings.DATA_DIR)
    operation = next((item for item in operations if item.id == operation_id), None)
    if operation is None:
        raise Http404("Операция не найдена.")
    return page("Операция", format_html("<p>{}</p><p>{}, {}, {}</p>",
                str(operation), operation.user.name, operation.account.name,
                operation.category.name))
