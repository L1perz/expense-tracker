from django.http import Http404
from django.shortcuts import render

from db import repository as data

from .forms import OperationFilterForm, StatisticsFilterForm


def operation_list(request):
    form = OperationFilterForm(request.GET)
    valid = form.is_valid()
    operations = data.get_operations(**form.cleaned_data) if valid else []
    return render(request, "operations/list.html", {
        "operations": operations,
        "total": sum(item["amount"] for item in operations),
        "form": form,
    }, status=200 if valid else 400)


def operation_detail(request, operation_id):
    operation = data.get_operation(operation_id)
    if operation is None:
        raise Http404("Операция не найдена.")
    return render(request, "operations/detail.html", {"operation": operation})


def statistics(request):
    form = StatisticsFilterForm(request.GET)
    valid = form.is_valid()
    context = data.get_statistics(**form.cleaned_data) if valid else {}
    return render(request, "operations/statistics.html", {
        **context, "form": form,
    }, status=200 if valid else 400)
