# -*- coding: utf-8 -*-

import re

from django.forms import ModelChoiceField
from django.forms import RegexField
from django.forms import Select
from django.forms import TextInput
from django.forms import ValidationError

from models import Mitglied

unicode_slug_re = re.compile(r'^[-\w]+$', re.UNICODE)

class UnicodeSlugField(RegexField):
    """
    Kann nicht SlugField nehmen, da dieses keine Unicode Zeichen versteht,
    ich aber in der URL Namen wie 'Fällbaum-Cup' haben möchte.
    (siehe django.forms.fields.SlugField)
    """
    default_error_messages = {
        'invalid': (u"Bitte nur Buchstaben und Ziffern (inklusive Bindestrich)"
                    u" eingeben"),
    }

    def __init__(self, *args, **kwargs):
        super(UnicodeSlugField, self).__init__(unicode_slug_re, *args, **kwargs)


class MitgliedSearchField(ModelChoiceField):

    def __init__(self, *args, **kwargs):
        kwargs['widget'] = kwargs.pop('widget', TextInput)
        super(MitgliedSearchField, self).__init__(*args, **kwargs)

    def clean(self, value):
        if self.required and not value:
            raise ValidationError(self.error_messages['required'])
        items = value.split()
        try:
            q = Mitglied.objects.filter(nummer=items[0])
            if q.count() == 0:
                # Falls Benutzer aus einer Liste von Mitgliedern gewählt hat
                primary_key = int(items[0])
                q = Mitglied.objects.filter(id=primary_key)
        except ValueError:
            if len(items) == 1:
                q = Mitglied.objects.filter(name__icontains=items[0])
            else:
                q = Mitglied.objects.filter(
                        name__icontains=items[0],
                        vorname__icontains=items[1])
        if q.count() == 0:
            text = u"Mitglied '%s' nicht gefunden. Bitte 'Name Vorname' oder 'Mitgliedernummer' eingeben" % (value,)
            raise ValidationError(text)
        elif q.count() > 1:
            text = u"Mitglied '%s' ist nicht eindeutig, bitte auswählen" % (value,)
            self.widget = Select()
            self.queryset = q
            raise ValidationError(text)
        else:
            return q[0]
