from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import AccountForm, CategoryForm, OperationForm, UserForm
from .models import Account, Category, Operation, User


@require_http_methods(["GET", "POST"])
def edit(request, kind, pk=None):
    model, form_type, destination, title = {
        "user": (User, UserForm, "homepage:users", "пользователя"),
        "category": (Category, CategoryForm, "homepage:categories", "категорию"),
        "account": (Account, AccountForm, "accounts:list", "счёт"),
        "operation": (Operation, OperationForm, "operations:list", "расход"),
    }[kind]
    instance = get_object_or_404(model, pk=pk) if pk is not None else None
    form = form_type(
        request.POST if request.method == "POST" else None,
        request.FILES if request.method == "POST" else None,
        instance=instance,
    )
    if request.method == "POST" and form.is_valid():
        try:
            saved = form.save()
        except ValidationError as error:
            form.add_error(
                None,
                error
                if not hasattr(error, "error_dict")
                else ValidationError(error.messages),
            )
        except DatabaseError:
            form.add_error(None, "Не удалось сохранить данные. Повторите попытку.")
        else:
            messages.success(request, "Изменения сохранены.")
            return redirect(
                saved.get_absolute_url()
                if hasattr(saved, "get_absolute_url")
                else destination
            )
    return render(
        request,
        "ledger/form.html",
        {
            "form": form,
            "title": f"{'Изменить' if instance else 'Добавить'} {title}",
            "cancel_url": destination,
        },
    )


@require_http_methods(["GET", "POST"])
def delete(request, kind, pk):
    model, destination = {
        "user": (User, "homepage:users"),
        "category": (Category, "homepage:categories"),
        "account": (Account, "accounts:list"),
    }[kind]
    instance = get_object_or_404(model, pk=pk)
    error = None
    if request.method == "POST":
        try:
            instance.delete()
        except ProtectedError:
            error = "Эта запись используется в счетах или операциях. Удалить её нельзя."
        else:
            messages.success(request, "Запись удалена.")
            return redirect(destination)
    return render(
        request,
        "ledger/confirm.html",
        {
            "object": instance,
            "title": "Удалить запись",
            "error": error,
            "cancel_url": destination,
            "button": "Удалить",
        },
    )


@require_http_methods(["POST"])
def cancel(request, operation_id):
    operation = get_object_or_404(Operation, pk=operation_id)
    try:
        operation.cancel()
    except (ValidationError, DatabaseError):
        messages.error(
            request,
            "Не удалось отменить расход. Обновите страницу и повторите действие.",
        )
    else:
        messages.success(request, "Расход отменён. Списанная сумма возвращена на счёт.")
    return redirect(operation)
