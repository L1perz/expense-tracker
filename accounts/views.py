from django.conf import settings
from django.http import Http404
from django.urls import reverse
from django.utils.html import format_html, format_html_join

from homepage.rendering import page
from models.accounts import find_account
from storage import load_project


def account_list(request):
    _, accounts, _, _ = load_project(settings.DATA_DIR)
    content = format_html_join("", '<p><a href="{}">{}</a></p>', (
        (reverse("accounts:detail", args=[account.id]), str(account))
        for account in accounts))
    return page("Счета", content or format_html("<p>Список пуст.</p>"))


def account_detail(request, account_id):
    _, accounts, _, _ = load_project(settings.DATA_DIR)
    try:
        account = find_account(accounts, account_id)
    except ValueError as error:
        raise Http404("Счёт не найден.") from error
    return page(account.name, format_html("<p>{}</p>", str(account)))
