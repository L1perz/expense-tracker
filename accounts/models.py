from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.text import slugify

from ledger.constants import MAX_MONEY
from users.models import User


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
        db_table = "ledger_account"
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
