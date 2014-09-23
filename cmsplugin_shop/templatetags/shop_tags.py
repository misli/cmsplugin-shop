from __future__ import unicode_literals

from django import template
from ..utils import currency as _currency

register = template.Library()

@register.filter
def currency(value):
    try:
        return _currency(value)
    except ValueError:
        return ''

