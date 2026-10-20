from django import forms

from homepage.forms import clean_money


class AccountFilterForm(forms.Form):
    max_balance = forms.CharField(
        label="Остаток не больше, руб.", required=False,
        widget=forms.TextInput(attrs={"inputmode": "decimal", "placeholder": "Любой"}),
    )

    def clean_max_balance(self):
        value = self.cleaned_data["max_balance"]
        return clean_money(value) if value else None
