from django.shortcuts import render

from ledger import queries as data
from ledger.models import Category, User


def index(request):
    accounts = data.accounts()
    operations = data.operations().active()
    return render(
        request,
        "homepage/index.html",
        {
            "accounts": accounts,
            "operations": operations[:5],
            "summary": data.summary(),
        },
    )


def user_list(request):
    return render(
        request,
        "ledger/directory.html",
        {
            "items": User.objects.all(),
            "title": "Пользователи",
            "create_url": "homepage:user_create",
            "edit_url": "homepage:user_edit",
            "delete_url": "homepage:user_delete",
        },
    )


def category_list(request):
    return render(
        request,
        "ledger/directory.html",
        {
            "items": Category.objects.all(),
            "title": "Категории расходов",
            "create_url": "homepage:category_create",
            "edit_url": "homepage:category_edit",
            "delete_url": "homepage:category_delete",
        },
    )


def page_not_found(request, exception):
    return render(request, "404.html", status=404)
