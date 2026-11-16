from django.contrib import admin
from accounts.admin import AccountInline
from operations.admin import OperationInline

from ledger.admin import UnicodeSearchAdmin
from .models import User


@admin.register(User)
class UserAdmin(UnicodeSearchAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    inlines = (AccountInline, OperationInline)
    list_per_page = 20
