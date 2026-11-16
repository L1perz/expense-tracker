from decimal import Decimal

from django import forms

from .models import MAX_MONEY, Account, Category, Operation, User


class StyledForm:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class UserForm(StyledForm, forms.ModelForm):
    class Meta:
        model = User
        fields = ("name",)


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
