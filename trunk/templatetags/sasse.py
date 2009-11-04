# -*- coding: utf-8 -*-

from django import template

register = template.Library()

@register.filter
def bewertung(value, einheit='PUNKT'):
    if value is None:
        return ''
    if einheit == 'ZEIT':
        return zeit2str(value)
    return value

def zeit2str(value):
    minutes = value // 60
    seconds = value - (minutes * 60)
    value = '%d:%.2f' % (minutes, seconds)
    return value

