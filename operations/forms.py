"""Проверка GET-параметров перед передачей значений в SQL."""

from django import forms

from db import repository
from homepage.forms import clean_money
from utils import validate_month


class MonthFilterForm(forms.Form):
    month = forms.CharField(
        label="Месяц", required=False, max_length=7,
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
    user_id = forms.TypedChoiceField(
        label="Пользователь", required=False, coerce=int, empty_value=None,
    )
    category_id = forms.TypedChoiceField(
        label="Категория", required=False, coerce=int, empty_value=None,
    )
    query = forms.CharField(label="Описание содержит", required=False, max_length=200)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user_id"].choices = [("", "Все пользователи")] + [
            (item["id"], item["name"]) for item in repository.get_users()]
        self.fields["category_id"].choices = [("", "Все категории")] + [
            (item["id"], item["name"]) for item in repository.get_categories()]


class StatisticsFilterForm(MonthFilterForm):
    min_total = forms.CharField(
        label="Расходы категории от, руб.", required=False,
        widget=forms.TextInput(attrs={"inputmode": "decimal", "placeholder": "0"}),
    )

    def clean_min_total(self):
        value = self.cleaned_data["min_total"]
        return clean_money(value) if value else 0
