"""Проверка GET-параметров перед передачей значений в SQL."""

from django import forms

from accounts.models import Account
from categories.models import Category
from operations.models import Operation
from users.models import User
from homepage.forms import clean_money
from utils import validate_month


class MonthFilterForm(forms.Form):
    month = forms.CharField(
        label="Месяц",
        required=False,
        max_length=7,
        widget=forms.TextInput(attrs={"type": "month"}),
    )

    def clean_month(self):
        value = self.cleaned_data["month"]
        if value:
            try:
                validate_month(value)
            except ValueError as error:
                raise forms.ValidationError(str(error)) from error
        return value


class OperationFilterForm(MonthFilterForm):
    date = forms.DateField(
        label="Дата", required=False, widget=forms.DateInput(attrs={"type": "date"})
    )
    account_id = forms.TypedChoiceField(
        label="Счёт", required=False, coerce=int, empty_value=None
    )
    status = forms.ChoiceField(
        label="Статус",
        required=False,
        choices=[("", "Кроме отменённых"), ("all", "Все")]
        + list(Operation.Status.choices),
    )
    sort = forms.ChoiceField(
        label="Порядок",
        required=False,
        choices=[
            ("", "Сначала новые"),
            ("date", "Сначала старые"),
            ("amount", "Сумма по возрастанию"),
            ("-amount", "Сумма по убыванию"),
            ("account", "По счёту"),
            ("user", "По пользователю"),
        ],
    )
    user_id = forms.TypedChoiceField(
        label="Пользователь",
        required=False,
        coerce=int,
        empty_value=None,
    )
    category_id = forms.TypedChoiceField(
        label="Категория",
        required=False,
        coerce=int,
        empty_value=None,
    )
    query = forms.CharField(label="Описание содержит", required=False, max_length=200)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user_id"].choices = [("", "Все пользователи")] + list(
            User.objects.values_list("id", "name")
        )
        self.fields["category_id"].choices = [("", "Все категории")] + list(
            Category.objects.values_list("id", "name")
        )
        self.fields["account_id"].choices = [("", "Все счета")] + list(
            Account.objects.values_list("id", "name")
        )


class StatisticsFilterForm(MonthFilterForm):
    min_total = forms.CharField(
        label="Расходы категории от, руб.",
        required=False,
        widget=forms.TextInput(attrs={"inputmode": "decimal", "placeholder": "0"}),
    )

    def clean_min_total(self):
        value = self.cleaned_data["min_total"]
        return clean_money(value) if value else 0
