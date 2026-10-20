from django import template

from utils import format_money

register = template.Library()


@register.filter
def money(cents):
    """Форматировать целые копейки без вычислений с float."""
    return format_money(int(cents or 0))
