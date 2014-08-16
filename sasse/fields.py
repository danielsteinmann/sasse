# -*- coding: utf-8 -*-

import re
from decimal import Decimal

from django.db.models import Q
from django.forms import Field
from django.forms import CharField
from django.forms import ModelChoiceField
from django.forms import RegexField
from django.forms import DecimalField
from django.forms import Select
from django.forms import TextInput
from django.forms import ValidationError

from models import Mitglied
from models import Schiffeinzel
from widgets import ZeitInSekundenWidget

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


class PunkteField(DecimalField):
    def __init__(self, bewertungsart, *args, **kwargs):
        max_value = None
        self.gueltige_werte = []
        self.gueltige_werte_str = bewertungsart.wertebereich
        if self.gueltige_werte_str != 'ALL':
            for v in self.gueltige_werte_str.split(','):
                value = Decimal(v.strip())
                if value > max_value:
                    max_value = value
                self.gueltige_werte.append(value)
        kwargs['max_digits'] = kwargs.pop('max_digits', 4)
        kwargs['decimal_places'] = kwargs.pop('decimal_places', 1)
        kwargs['min_value'] = kwargs.pop('min_value', Decimal('0'))
        kwargs['max_value'] = kwargs.pop('max_value', max_value)
        super(PunkteField, self).__init__(*args, **kwargs)
        self.widget.attrs['size'] = 4

    def clean(self, value):
        value = super(PunkteField, self).clean(value)
        if self.gueltige_werte and value not in self.gueltige_werte:
            msg = u'Nur folgende Zahlen sind erlaubt: %s' % self.gueltige_werte_str
            raise ValidationError(msg)
        return value


zeit_parser = re.compile(r"((?P<min>\d+)[: .])?(?P<sec>\d+)(\.(?P<frac>\d+))?$")

class ZeitInSekundenField(Field):
    """
    Wandelt die Eingabe von Minuten/Sekunden/Hundertstel in einen Decimal, der
    die Anzahl Sekunden representiert.
    """
    widget = ZeitInSekundenWidget(attrs={'size': 7})
    default_error_messages = {
        'invalid': (u"Ungültige Eingabe. Bitte Zeit im Format"
                    u" 'min:sek.hundertstel' eingeben."
                    u" Beispiel: '2:35.76' für 2 Minuten, 35 Sekunden und"
                    u" 76 Hunderstel. Der Wert '2.35.76' ist auch ok.")
    }

    def clean(self, value):
        super(ZeitInSekundenField, self).clean(value)
        m = zeit_parser.match(value)
        if m is None:
            raise ValidationError(self.error_messages['invalid'])
        minutes = m.group('min') or '0'
        seconds = m.group('sec')
        fractional_second = m.group('frac') or ''
        if minutes != '0' and fractional_second == '' and '.' in value:
            # Weil der Punkt als Separator zwischen Minuten und Sekunden aus
            # Datenerfassungsgründen auch erlaubt ist, muss man in diesem Fall
            # die Minuten/Sekunden in Sekunden/Millis umbiegen
            fractional_second = seconds
            seconds = minutes
            minutes = '0'
        total_seconds = int(minutes)*60 + int(seconds)
        result = Decimal("%d.%s" % (total_seconds, fractional_second))
        if result == 0:
            msg = 'Zeit muss grösser 0 sein.'
            raise ValidationError(msg)
        return result


class MitgliedSearchField(ModelChoiceField):
    """
    Ein Mitglied kann mit einem beliebigen Text (z.B. Name oder
    Mitgliedernummer) eingebeben werden.

    Dieses Feld ist nötig, weil ein normales ModelChoiceField mehr als 2000
    Einträge hätte und somit die HTML Seite aufbläst. Zudem ist es nun möglich,
    neben der Mitgliedernummer auch nur Namen/Vornamen einzugeben.
    """
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
                q = Mitglied.objects.filter(
                        Q(name__icontains=items[0])
                        | Q(vorname__icontains=items[0])
                        | Q(sektion__name__icontains=items[0]))
            else:
                q = Mitglied.objects.filter(
                        name__icontains=items[0],
                        vorname__icontains=items[1])
        if q.count() == 0:
            text = u"Mitglied '%s' nicht gefunden. Bitte 'Name Vorname' oder 'Mitgliedernummer' eingeben" % (value,)
            raise ValidationError(text)
        elif q.count() > 1:
            text = u"'%s' ist nicht eindeutig, bitte auswählen" % (value,)
            self.widget = Select()
            self.queryset = q
            raise ValidationError(text)
        else:
            return q[0]

    def value_for_form(self, mitglied):
        result = None
        if mitglied:
            # Falls während clean() ein einzelnes Mitglied gefunden wurde, soll
            # die Text Repräsentation davon (und nicht nur die Nummer oder
            # andere eingegbene Suchkriterien) dargestellt werden. Somit ist
            # dem Benutzer klar, welches Mitglied gefunden wurde.
            result = u" ".join([mitglied.nummer, mitglied.name, mitglied.vorname])
            self.widget.attrs['size'] = len(result) + 2
        else:
            # clean() hat nichts oder nichts oder nichts eindeutiges gefunden
            if isinstance(self.widget, Select):
                result = self.queryset[0].id
        return result


startnummern_re = re.compile(r'^[- ,\d]+$', re.UNICODE)

class StartnummernSelectionField(RegexField):
    """
    Erlaubt die Eingabe einer beliebigen Menge von Startnummern.
    """
    help_text = u"Beispiele: '1-6,9' oder '600-'"
    default_error_messages = {
        'invalid': u"Bitte nur ganze Zahlen, Bindestrich oder Komma eingeben",
    }
    def __init__(self, disziplin, *args, **kwargs):
        super(StartnummernSelectionField, self).__init__(startnummern_re, *args, **kwargs)
        self.disziplin = disziplin
        self.widget.attrs['size'] = 7
        self.required = False

    # Vorschlag für andere Implementation:
    #
    #   input = '1,3,5,1-20,30-50,-100,500-'
    #   [
    #      ('in', [1,3,5]),
    #      ('range', [1,20]),
    #      ('range', [30,50]),
    #      ('gte', 100),
    #      ('lte', 500),
    #   ]
    #
    # Mehrfache Eingabe von 'lte' und 'gte' ergeben ValidationError. 
    #  (Beispiel: '50-,80-' => ValidationError, nur ein gte erlaubt)
    #  (Beispiel: '-50-,-80' => ValidationError, nur ein lte erlaubt)
    #  (Beispiel: '50-,-80' => ValidationError, nur lte oder gte erlaubt. Range verwenden)
    #
    # Mehrfache Eingabe von einzelnen Startnummer erzeugen ein einziges 'in'
    #  (Beispiel: '1,2,5-10,12' => [('in', [1,2,5,12]), ('range', [5,10])])
    #
    # Ein Bereich kann mehrfach vorkommen
    #  (Beispiel: '5-10,13-15' => [('range', [5,10]), ('range', [13,15])])
    #
    # TODO: Reihenfolge beibehalten. 
    #  (Beispiel: '1,3,2,5' => [('range', [1,3,2,5]))
    #  Wichtig ist hier, dass die Datenbank die Startnummern in zufälliger
    #  Reihenfolge sendet, aber der Benutzer die Nummern in spezifischer
    #  Reihenfolge haben möchte.
    #
    def clean(self, value):
        super(StartnummernSelectionField, self).clean(value)
        result = Schiffeinzel.objects.filter(disziplin=self.disziplin)
        if value and value.strip():
            queries = []
            commas = value.split(',')
            for c in commas:
                if c == '':
                    text = u"Ein Komma ohne Zahl links und rechts ist nicht gültig."
                    raise ValidationError(text)
                dashes = c.split('-')
                if len(dashes) == 1:
                    queries.append(Q(startnummer=int(c)))
                elif len(dashes) > 2:
                    text = u"'%s' enthält mehr als einen Gedankenstrich." % (c,)
                    raise ValidationError(text)
                else:
                    from_nr = dashes[0]
                    until_nr = dashes[1]
                    if from_nr == '' and until_nr == '':
                        text = u"Ein Gedankenstrich ohne Zahl links oder rechts ist nicht gültig."
                        raise ValidationError(text)
                    elif until_nr == '':
                        queries.append(Q(startnummer__gte=from_nr))
                    elif from_nr == '':
                        queries.append(Q(startnummer__lte=until_nr))
                    else:
                        queries.append(Q(startnummer__range=dashes))
            query = queries.pop()
            for item in queries:
                query |= item
            result = result.filter(query)
            if not result:
                text = u"Keine Schiffe mit dieser Eingabe von Startnummern gefunden."
                raise ValidationError(text)

        return result
