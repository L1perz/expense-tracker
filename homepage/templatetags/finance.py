from django import template

from utils import format_money

register = template.Library()


@register.filter
def money(cents):
    """Форматировать целые копейки без вычислений с float."""
    return format_money(int(cents or 0))


@register.filter
def rubles(cents):
    value = int(cents or 0)
    whole, fraction = divmod(abs(value), 100)
    grouped = f"{whole:,}".replace(",", "\u202f")
    return f"{'−' if value < 0 else ''}{grouped},{fraction:02d}"
