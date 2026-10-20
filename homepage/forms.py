from django import forms

from utils import money_to_cents


def clean_money(value):
    try:
        return money_to_cents(value, allow_zero=True)
    except ValueError as error:
        raise forms.ValidationError(str(error)) from error
