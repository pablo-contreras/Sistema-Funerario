from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def clp(value):
    try:
        amount = Decimal(value or 0)
    except (InvalidOperation, TypeError, ValueError):
        return "$0"
    return f"${amount:,.0f}".replace(",", ".")


@register.filter
def value_or_line(value):
    return value if value not in (None, "") else "________________"
