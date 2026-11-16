from django.shortcuts import render

from .models import User


def user_list(request):
    return render(
        request,
        "ledger/directory.html",
        {
            "items": User.objects.all(),
            "title": "Пользователи",
            "create_url": "users:create",
            "edit_url": "users:edit",
            "delete_url": "users:delete",
        },
    )
