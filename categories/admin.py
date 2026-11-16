from django.contrib import admin
from categories.forms import CategoryForm
from operations.admin import OperationInline

from ledger.admin import UnicodeSearchAdmin
from .models import Category


@admin.register(Category)
class CategoryAdmin(UnicodeSearchAdmin):
    form = CategoryForm
    list_display = ("id", "name")
    search_fields = ("name",)
    inlines = (OperationInline,)
    list_per_page = 20
