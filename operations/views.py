from django.http import Http404
from django.core.paginator import Paginator
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, render

from ledger import queries as data

from .forms import OperationFilterForm, StatisticsFilterForm


def operation_list(request):
    form = OperationFilterForm(request.GET)
    valid = form.is_valid()
    operations = data.operations()
    if valid:
        values = form.cleaned_data
        operations = data.period(operations, values["month"])
        if values["date"]:
            operations = operations.for_date(values["date"])
        for name in ("user_id", "account_id", "category_id"):
            if values[name]:
                operations = operations.filter(**{name: values[name]})
        if values["query"]:
            operations = operations.search(values["query"])
        if values["status"] not in ("all", ""):
            operations = operations.filter(status=values["status"])
        elif not values["status"]:
            operations = operations.active()
        sort = {
            "": "-date",
            "date": "date",
            "amount": "amount",
            "-amount": "-amount",
            "account": "account__name",
            "user": "user__name",
        }[values["sort"]]
        operations = operations.order_by(sort, "-pk")
    else:
        operations = operations.none()
    total = operations.completed().aggregate(total=Coalesce(Sum("amount"), 0))["total"]
    page = Paginator(operations, 5).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    return render(
        request,
        "operations/list.html",
        {
            "operations": page.object_list,
            "page_obj": page,
            "query_params": params.urlencode(),
            "total": total,
            "form": form,
        },
        status=200 if valid else 400,
    )


def operation_detail(request, operation_id):
    if operation_id > 2**63 - 1:
        raise Http404("Операция не найдена.")
    operation = get_object_or_404(data.operations(), pk=operation_id)
    return render(request, "operations/detail.html", {"operation": operation})


def statistics(request):
    form = StatisticsFilterForm(request.GET)
    valid = form.is_valid()
    context = data.statistics(**form.cleaned_data) if valid else {}
    return render(
        request,
        "operations/statistics.html",
        {
            **context,
            "form": form,
        },
        status=200 if valid else 400,
    )
