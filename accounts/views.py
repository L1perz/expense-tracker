from django.http import Http404
from django.shortcuts import get_object_or_404, render

from ledger import queries as data

from .forms import AccountFilterForm


def account_list(request):
    form = AccountFilterForm(request.GET)
    valid = form.is_valid()
    accounts = data.accounts()
    if valid and form.cleaned_data["max_balance"] is not None:
        accounts = accounts.filter(balance__lte=form.cleaned_data["max_balance"])
    if not valid:
        accounts = accounts.none()
    return render(
        request,
        "accounts/list.html",
        {
            "accounts": accounts,
            "form": form,
        },
        status=200 if valid else 400,
    )


def account_detail(request, account_id=None, slug=None):
    if account_id is not None and account_id > 2**63 - 1:
        raise Http404("Счёт не найден.")
    account = get_object_or_404(
        data.accounts(),
        **({"pk": account_id} if account_id is not None else {"slug": slug}),
    )
    operations = data.operations().filter(account=account)
    return render(
        request,
        "accounts/detail.html",
        {
            "account": account,
            "operations": operations,
        },
    )
