"""Фильтрация, создание и редактирование расходов."""

from decimal import Decimal

from django import forms

from ledger.constants import MAX_MONEY
from ledger.forms import StyledForm

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


class OperationForm(StyledForm, forms.ModelForm):
    amount = forms.DecimalField(
        label="Сумма, руб.",
        max_digits=12,
        decimal_places=2,
        localize=True,
        min_value=Decimal("0.01"),
        help_text="Например, 750,50. Не более двух знаков после запятой.",
    )

    class Meta:
        model = Operation
        fields = (
            "user",
            "account",
            "category",
            "amount",
            "date",
            "description",
            "status",
        )
        widgets = {
            "date": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "description": forms.TextInput(
                attrs={"placeholder": "Например, продукты на неделю"}
            ),
        }
        help_texts = {
            "status": "Оплаченный расход списывает деньги, отменённый возвращает их."
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["account"].queryset = Account.objects.select_related("user")
        if self.instance.pk:
            self.initial["amount"] = Decimal(self.instance.amount) / 100

    def clean_amount(self):
        amount = int(self.cleaned_data["amount"] * 100)
        if amount > MAX_MONEY:
            raise forms.ValidationError("Слишком большая сумма.")
        return amount

    def clean(self):
        data = super().clean()
        account, user = data.get("account"), data.get("user")
        if account and user and account.user_id != user.pk:
            self.add_error("account", "Счёт не принадлежит выбранному пользователю.")
        if (
            account
            and data.get("amount")
            and data.get("status") == Operation.Status.COMPLETED
        ):
            available = account.balance
            old = (
                Operation.objects.filter(pk=self.instance.pk).first()
                if self.instance.pk
                else None
            )
            if (
                old
                and old.account_id == account.pk
                and old.status == Operation.Status.COMPLETED
            ):
                available += old.amount
            if data["amount"] > available:
                raise forms.ValidationError("На выбранном счёте недостаточно денег.")
        return data
