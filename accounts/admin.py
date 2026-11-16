from django.contrib import admin
from django.utils.html import format_html

from accounts.forms import AccountForm
from operations.admin import OperationInline
from utils import format_money

from ledger.admin import UnicodeSearchAdmin
from .models import Account


class AccountInline(admin.TabularInline):
    model = Account
    extra = 0
    fields = ("name", "balance")
    readonly_fields = fields
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Account)
class AccountAdmin(UnicodeSearchAdmin):
    form = AccountForm
    list_display = ("name", "user", "current_balance")
    search_fields = ("name", "user__name")
    list_filter = ("user",)
    list_select_related = ("user",)
    readonly_fields = ("balance", "slug", "preview")
    inlines = (OperationInline,)
    ordering = ("name",)
    list_per_page = 20

    def get_fields(self, request, obj=None):
        return (
            "user",
            "name",
            "balance" if obj else "opening_balance",
            "image",
            "slug",
            "preview",
        )

    @admin.display(description="Остаток")
    def current_balance(self, obj):
        return format_money(obj.balance)

    @admin.display(description="Изображение")
    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" alt="" style="max-width:160px">', obj.image.url
            )
        return "Без изображения"
