from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

from django import template
from ..utils import currency as _currency

register = template.Library()

@register.filter
def currency(value):
    try:
        return _currency(value)
    except ValueError:
        return ''

