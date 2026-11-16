from django.shortcuts import render

from .models import Category


def category_list(request):
    return render(
        request,
        "ledger/directory.html",
        {
            "items": Category.objects.all(),
            "title": "Категории расходов",
            "create_url": "categories:create",
            "edit_url": "categories:edit",
            "delete_url": "categories:delete",
        },
    )
