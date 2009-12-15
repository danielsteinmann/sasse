# -*- coding: utf-8 -*-

from decimal import Decimal
from django import template

register = template.Library()

@register.filter
def bewertung(value, einheit='PUNKT'):
    if value is None:
        return ''
    elif einheit == 'ZEIT':
        return zeit2str(value)
    else:
        if value == 0:
            return '0'
        return '%.01f' % value

def zeit2str(value):
    assert isinstance(value, Decimal)
    minutes = value // 60
    fractional_seconds = value - (minutes * 60)
    seconds = fractional_seconds // 1
    millis = (fractional_seconds - seconds) * 100
    value = '%d:%02d.%02d' % (minutes, seconds, millis)
    return value

