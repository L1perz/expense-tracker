from django.contrib import admin
from django.utils.text import smart_split, unescape_string_literal

from .db_functions import search_text


class UnicodeSearchAdmin(admin.ModelAdmin):
    def get_search_results(self, request, queryset, search_term):
        fields = self.get_search_fields(request)
        if fields and search_term:
            for term in smart_split(search_term):
                if term.startswith(('"', "'")) and term[0] == term[-1]:
                    term = unescape_string_literal(term)
                queryset = search_text(queryset, fields, term)
        # В search_fields используются только собственные поля и связи ForeignKey.
        return queryset, False


admin.site.site_header = "Управление расходами"
admin.site.site_title = "Расходы"
admin.site.index_title = "Счета и операции"
