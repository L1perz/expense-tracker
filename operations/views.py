from django.http import Http404
from django.shortcuts import render

from homepage import data


def operation_list(request):
    operations = data.get_operations()
    return render(request, "operations/list.html", {
        "operations": operations,
        "total": sum(item["amount"] for item in operations),
    })


def operation_detail(request, operation_id):
    operation = next((item for item in data.get_operations()
                      if item["id"] == operation_id), None)
    if operation is None:
        raise Http404("Операция не найдена.")
    return render(request, "operations/detail.html", {"operation": operation})
