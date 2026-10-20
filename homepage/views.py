from django.shortcuts import render

from . import data


def index(request):
    accounts = data.get_accounts()
    operations = data.get_operations()
    return render(request, "homepage/index.html", {
        "accounts": accounts, "operations": operations[:5],
        "summary": {"balance": sum(item["balance"] for item in accounts),
                    "total": sum(item["amount"] for item in operations),
                    "count": len(operations)},
    })


def user_list(request):
    return render(request, "homepage/users.html", {"users": data.get_users()})


def category_list(request):
    return render(request, "homepage/categories.html", {
        "categories": data.get_categories(),
    })


def page_not_found(request, exception):
    return render(request, "404.html", status=404)
