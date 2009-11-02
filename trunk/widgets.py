# -*- coding: utf-8 -*-

from decimal import Decimal

from django.forms.widgets import Input

class ZeitInSekundenWidget(Input):
    input_type = 'text'

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        elif isinstance(value, Decimal):
            minutes = value // 60
            seconds = value - (minutes * 60)
            value = '%d:%.2f' % (minutes, seconds)
        return super(ZeitInSekundenWidget, self).render(name, value, attrs)

