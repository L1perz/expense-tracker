from django import forms

from ledger.forms import StyledForm
from .models import Category


class CategoryForm(StyledForm, forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name",)

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if (
            Category.objects.filter(name_key=name.casefold())
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise forms.ValidationError("Такая категория уже есть.")
        return name
