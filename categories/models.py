from django.core.exceptions import ValidationError
from django.db import models


class Category(models.Model):
    name = models.CharField("Название", max_length=100)
    name_key = models.CharField(max_length=100, unique=True, editable=False, blank=True)

    class Meta:
        db_table = "ledger_category"
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
