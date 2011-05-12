# -*- coding: utf-8 -*-

from decimal import Decimal

from django.forms.widgets import Input
from templatetags.sasse import zeit2str

class ZeitInSekundenWidget(Input):
    input_type = 'text'

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        elif isinstance(value, Decimal):
            value = zeit2str(value)
        return super(ZeitInSekundenWidget, self).render(name, value, attrs)
