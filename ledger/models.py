"""Счета и расходы. Списание и возврат денег выполняются одной транзакцией."""

from collections import defaultdict
from datetime import date

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.db.models import F, Q
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from .db_functions import UnicodeCasefold

MAX_MONEY = 999_999_999_999


class User(models.Model):
    name = models.CharField("Имя", max_length=100)

    class Meta:
        ordering = ("name", "pk")
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField("Название", max_length=100)
    name_key = models.CharField(max_length=100, unique=True, editable=False, blank=True)

    class Meta:
        ordering = ("name", "pk")
        verbose_name = "категория"
        verbose_name_plural = "категории"

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        self.name = self.name.strip()
        self.name_key = self.name.casefold()
        if not self.name:
            raise ValidationError({"name": "Введите название категории."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Account(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="accounts", verbose_name="Владелец"
    )
    name = models.CharField("Название", max_length=100)
    balance = models.BigIntegerField(
        "Остаток, коп.",
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(MAX_MONEY)],
    )
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    image = models.ImageField("Изображение", upload_to="accounts/%Y/%m/", blank=True)

    class Meta:
        ordering = ("name", "pk")
        constraints = [
            models.CheckConstraint(
                condition=Q(balance__gte=0, balance__lte=MAX_MONEY),
                name="account_balance_range",
            )
        ]
        verbose_name = "счёт"
        verbose_name_plural = "счета"

    def __str__(self):
        return f"{self.name} — {self.user.name}"

    def clean(self):
        super().clean()
        if self.pk and self.operations.exists():
            original = Account.objects.get(pk=self.pk)
            if original.user_id != self.user_id:
                raise ValidationError(
                    {"user": "У счёта с операциями нельзя менять владельца."}
                )

    def save(
        self, *, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if not self.slug:
            # UUID avoids collisions and keeps Cyrillic account names supported.
            from uuid import uuid4

            self.slug = f"{slugify(self.name) or 'account'}-{uuid4().hex[:12]}"
        editing = not self._state.adding and not force_insert
        if editing:
            if update_fields is not None:
                update_fields = set(update_fields)
                if "balance" in update_fields:
                    raise ValidationError(
                        "Остаток счёта меняется только через операции."
                    )
            else:
                # Не записываем старый остаток при изменении реквизитов счёта.
                deferred = self.get_deferred_fields()
                update_fields = {
                    field.name
                    for field in self._meta.concrete_fields
                    if not field.primary_key
                    and field.name != "balance"
                    and field.attname not in deferred
                }
        self.full_clean(exclude=["balance"] if editing else None)
        result = super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )
        if editing:
            self.refresh_from_db(using=using, fields=["balance"])
        return result

    def get_absolute_url(self):
        return reverse("accounts:detail_slug", kwargs={"slug": self.slug})


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
        text = text.casefold()
        return self.alias(
            search_description=UnicodeCasefold("description"),
            search_account=UnicodeCasefold("account__name"),
            search_category=UnicodeCasefold("category__name"),
            search_user=UnicodeCasefold("user__name"),
        ).filter(
            Q(search_description__contains=text)
            | Q(search_account__contains=text)
            | Q(search_category__contains=text)
            | Q(search_user__contains=text)
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
        ordering = ("-date", "-pk")
        indexes = [models.Index(fields=["status", "date"])]
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
