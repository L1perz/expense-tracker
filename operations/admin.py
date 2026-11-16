from django.contrib import admin
from ledger.forms import OperationForm

from ledger.admin import UnicodeSearchAdmin
from .models import Operation


class OperationInline(admin.TabularInline):
    model = Operation
    extra = 0
    fields = ("description", "amount", "date", "status")
    readonly_fields = fields
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Operation)
class OperationAdmin(UnicodeSearchAdmin):
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
