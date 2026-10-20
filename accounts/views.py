from django.http import Http404
from django.shortcuts import render

from homepage import data


def account_list(request):
    return render(request, "accounts/list.html", {"accounts": data.get_accounts()})


def account_detail(request, account_id):
    account = next((item for item in data.get_accounts()
                    if item["id"] == account_id), None)
    if account is None:
        raise Http404("Счёт не найден.")
    operations = [item for item in data.get_operations()
                  if item["account_id"] == account_id]
    return render(request, "accounts/detail.html", {
        "account": account, "operations": operations,
    })
