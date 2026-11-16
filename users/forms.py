from django import forms

from ledger.forms import StyledForm
from .models import User


class UserForm(StyledForm, forms.ModelForm):
    class Meta:
        model = User
        fields = ("name",)
