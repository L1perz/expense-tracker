"""Небольшой общий набор SVG-иконок и навигация по страницам."""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()
PATHS = {
    "overview": (
        '<rect x="3" y="3" width="7" height="7" rx="1.5"/>'
        '<rect x="14" y="3" width="7" height="7" rx="1.5"/>'
        '<rect x="3" y="14" width="7" height="7" rx="1.5"/>'
        '<rect x="14" y="14" width="7" height="7" rx="1.5"/>'
    ),
    "account": (
        '<rect x="3" y="5" width="18" height="14" rx="3"/>'
        '<path d="M3 10h18M7 15h3"/>'
    ),
    "operations": '<path d="M4 7h15m-4-4 4 4-4 4M20 17H5m4-4-4 4 4 4"/>',
    "statistics": '<path d="M4 20h17M7 16v-5m6 5V5m6 11v-8"/>',
    "users": (
        '<circle cx="9" cy="8" r="3"/>'
        '<path d="M3 20v-2a6 6 0 0 1 12 0v2m1-15a3 3 0 0 1 0 6'
        'm2 3a5 5 0 0 1 3 4v2"/>'
    ),
    "category": '<path d="M3 4h8l10 10-7 7L3 10Z"/><circle cx="7" cy="8" r="1"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "arrow": '<path d="M5 12h14m-6-6 6 6-6 6"/>',
    "back": '<path d="M19 12H5m6-6-6 6 6 6"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
    "filter": (
        '<path d="M4 7h16M4 17h16"/><circle cx="8" cy="7" r="2"/>'
        '<circle cx="16" cy="17" r="2"/>'
    ),
    "edit": '<path d="m15 4 5 5M4 20l5-1L21 7l-5-5L4 14Z"/>',
    "settings": (
        '<circle cx="12" cy="12" r="3"/>'
        '<path d="m9 3-1 3-3 1-2 5 2 5 3 1 1 3h6l1-3 3-1 2-5-2-5-3-1-1-3Z"/>'
    ),
    "chevron": '<path d="m8 10 4 4 4-4"/>',
}


@register.simple_tag
def icon(name):
    paths = PATHS.get(name, PATHS["account"])
    return mark_safe(
        '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" '
        'aria-hidden="true" focusable="false">' + paths + '</svg>'
    )


@register.simple_tag
def page_numbers(page):
    return page.paginator.get_elided_page_range(page.number, on_each_side=1, on_ends=1)
