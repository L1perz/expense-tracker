from collections import defaultdict
from datetime import date

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.db.models import F, Q
from django.urls import reverse
from django.utils import timezone

from accounts.models import Account
from categories.models import Category
from ledger.constants import MAX_MONEY
from ledger.db_functions import search_text
from users.models import User


class OperationQuerySet(models.QuerySet):
    def active(self):
        return self.exclude(status=Operation.Status.CANCELLED)

    def completed(self):
        return self.filter(status=Operation.Status.COMPLETED)

    def cancelled(self):
        return self.filter(status=Operation.Status.CANCELLED)

    def for_date(self, day):
        return self.filter(date=day)

    def with_details(self):
        return self.select_related("user", "account__user", "category")

    def search(self, text):
        return search_text(
            self, ("description", "account__name", "category__name", "user__name"), text
        )

    def update(self, **kwargs):
        raise ValidationError(
            "Изменяйте операции через save(): баланс обновляется вместе с расходом."
        )

    def delete(self):
        count = 0
        with transaction.atomic():
            for operation in self:
                deleted, _ = operation.delete()
                count += deleted
        return count, {self.model._meta.label: count}


class Operation(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Запланирован"
        COMPLETED = "completed", "Оплачен"
        CANCELLED = "cancelled", "Отменён"

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="operations",
        verbose_name="Пользователь",
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="operations",
        verbose_name="Счёт",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="operations",
        verbose_name="Категория",
    )
    amount = models.BigIntegerField(
        "Сумма, коп.", validators=[MinValueValidator(1), MaxValueValidator(MAX_MONEY)]
    )
    date = models.DateField("Дата", default=timezone.localdate)
    description = models.CharField("Описание", max_length=300)
    status = models.CharField(
        "Статус", max_length=12, choices=Status, default=Status.COMPLETED
    )
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    is_large = models.GeneratedField(
        expression=models.Case(
            models.When(amount__gte=1_000_000, then=True), default=False
        ),
        output_field=models.BooleanField(),
        db_persist=True,
        verbose_name="От 10 000 руб.",
    )

    objects = OperationQuerySet.as_manager()

    class Meta:
        db_table = "ledger_operation"
        ordering = ("-date", "-pk")
        indexes = [
            models.Index(
                fields=["status", "date"], name="ledger_oper_status_da446b_idx"
            )
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0, amount__lte=MAX_MONEY),
                name="operation_amount_range",
            ),
            models.CheckConstraint(
                condition=Q(status__in=["pending", "completed", "cancelled"]),
                name="operation_status_valid",
            ),
        ]
        verbose_name = "операция"
        verbose_name_plural = "операции"

    def __str__(self):
        return f"{self.date}: {self.description}"

    def clean(self):
        super().clean()
        if self.account_id and self.user_id:
            owner = (
                Account.objects.filter(pk=self.account_id)
                .values_list("user_id", flat=True)
                .first()
            )
            if owner is not None and owner != self.user_id:
                raise ValidationError(
                    {"account": "Счёт не принадлежит выбранному пользователю."}
                )
        if (
            isinstance(self.date, date)
            and self.status == self.Status.COMPLETED
            and self.date > timezone.localdate()
        ):
            raise ValidationError(
                {"date": "Для будущего расхода выберите статус «Запланирован»."}
            )

    def save(self, *args, **kwargs):
        if kwargs.get("update_fields"):
            raise ValidationError(
                "Операция сохраняется целиком вместе с изменением баланса."
            )
        with transaction.atomic():
            old = (
                Operation.objects.select_for_update().filter(pk=self.pk).first()
                if self.pk
                else None
            )
            self.full_clean()
            adjustments = defaultdict(int)
            if old and old.status == self.Status.COMPLETED:
                adjustments[old.account_id] += old.amount
            if self.status == self.Status.COMPLETED:
                adjustments[self.account_id] -= self.amount
            for account in (
                Account.objects.select_for_update()
                .filter(pk__in=adjustments)
                .order_by("pk")
            ):
                delta = adjustments[account.pk]
                if not 0 <= account.balance + delta <= MAX_MONEY:
                    raise ValidationError(
                        "На счёте недостаточно денег или превышен предел баланса."
                    )
                if delta and not Account.objects.filter(
                    pk=account.pk, balance=account.balance
                ).update(balance=F("balance") + delta):
                    raise ValidationError(
                        "Баланс изменился. Обновите страницу и повторите действие."
                    )
            return super().save(*args, **kwargs)

    def cancel(self):
        with transaction.atomic():
            # Отмена использует актуальную сумму и счёт, а не старый объект из вкладки.
            self.refresh_from_db(from_queryset=Operation.objects.select_for_update())
            if self.status != self.Status.CANCELLED:
                self.status = self.Status.CANCELLED
                self.save()

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            current = Operation.objects.select_for_update().get(pk=self.pk)
            if current.status != self.Status.CANCELLED:
                raise ValidationError(
                    "Сначала отмените операцию, чтобы сохранить корректный баланс."
                )
            return super().delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("operations:detail", kwargs={"operation_id": self.pk})
