from django.http import Http404
from django.shortcuts import render

from db import repository as data

from .forms import AccountFilterForm


def account_list(request):
    form = AccountFilterForm(request.GET)
    valid = form.is_valid()
    accounts = data.get_accounts(form.cleaned_data["max_balance"]) if valid else []
    return render(request, "accounts/list.html", {
        "accounts": accounts, "form": form,
    }, status=200 if valid else 400)


def account_detail(request, account_id):
    account = data.get_account(account_id)
    if account is None:
        raise Http404("Счёт не найден.")
    operations = data.get_operations(account_id=account_id)
    return render(request, "accounts/detail.html", {
        "account": account, "operations": operations,
    })
