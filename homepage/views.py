from django.shortcuts import render

from ledger import queries as data


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


def page_not_found(request, exception):
    return render(request, "404.html", status=404)
