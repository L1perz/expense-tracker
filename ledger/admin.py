from django.contrib import admin
from django.utils.html import format_html

from .forms import AccountForm, OperationForm
from .models import Account, Category, Operation, User
from utils import format_money


class OperationInline(admin.TabularInline):
    model = Operation
    extra = 0
    fields = ("description", "amount", "date", "status")
    readonly_fields = fields
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


class AccountInline(admin.TabularInline):
    model = Account
    extra = 0
    fields = ("name", "balance")
    readonly_fields = fields
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    inlines = (AccountInline, OperationInline)
    list_per_page = 20


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    inlines = (OperationInline,)
    list_per_page = 20


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
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


@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    form = OperationForm
    list_display = (
        "description",
        "user",
        "account",
        "category",
        "date",
        "status",
        "is_large",
    )
    list_filter = ("status", "date", "category", "account__user")
    search_fields = ("description", "account__name", "user__name", "category__name")
    list_select_related = ("user", "account", "category")
    ordering = ("-date", "-pk")
    list_per_page = 20
    readonly_fields = ("created_at", "is_large")
    actions = None

    def has_delete_permission(self, request, obj=None):
        return bool(obj and obj.status == Operation.Status.CANCELLED)


admin.site.site_header = "Управление расходами"
admin.site.site_title = "Расходы"
admin.site.index_title = "Счета и операции"
