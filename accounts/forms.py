from django import forms

from homepage.forms import clean_money
from ledger.forms import StyledForm
from .models import Account


class AccountFilterForm(forms.Form):
    max_balance = forms.CharField(
        label="Остаток не больше, руб.",
        required=False,
        widget=forms.TextInput(attrs={"inputmode": "decimal", "placeholder": "Любой"}),
    )

    def clean_max_balance(self):
        value = self.cleaned_data["max_balance"]
        return clean_money(value) if value else None


class AccountForm(StyledForm, forms.ModelForm):
    opening_balance = forms.DecimalField(
        label="Начальный баланс, руб.",
        max_digits=12,
        decimal_places=2,
        localize=True,
        min_value=0,
        initial=0,
        help_text="После создания остаток меняется через операции.",
    )

    class Meta:
        model = Account
        fields = ("user", "name", "opening_balance", "image")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields.pop("opening_balance")

    def save(self, commit=True):
        account = super().save(commit=False)
        if not account.pk:
            account.balance = int(self.cleaned_data["opening_balance"] * 100)
        if commit:
            account.save()
        return account
