from django.db import models


class User(models.Model):
    name = models.CharField("Имя", max_length=100)

    class Meta:
        db_table = "ledger_user"
        ordering = ("name", "pk")
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self):
        return self.name
