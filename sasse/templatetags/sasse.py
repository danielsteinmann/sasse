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

@register.filter
def fahrerpaar_alter(td):
    return round(td.days / 365.2425, 1)

@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    '''
    Returns the URL-encoded querystring for the current page,
    updating the params with the key/value pairs passed to the tag.

    E.g: given the querystring ?foo=1&bar=2
    {% query_transform bar=3 %} outputs ?foo=1&bar=3
    {% query_transform foo='baz' %} outputs ?foo=baz&bar=2
    {% query_transform foo='one' bar='two' baz=99 %} outputs ?foo=one&bar=two&baz=99

    A RequestContext is required for access to the current querystring.

    See https://stackoverflow.com/questions/46026268/pagination-and-get-parameters
    '''
    query = context['request'].GET.copy()
    for k, v in kwargs.items():
        query[k] = v
    return query.urlencode()
