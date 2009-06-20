# -*- coding: utf-8 -*-

import re

from django.db.models import Q
from django.forms import CharField
from django.forms import Form
from django.forms import HiddenInput
from django.forms import ModelChoiceField
from django.forms import ModelForm
from django.forms import RegexField
from django.forms import Select
from django.forms import TextInput
from django.forms import ValidationError

from models import Disziplin
from models import Kategorie
from models import Mitglied
from models import Posten
from models import Postenart
from models import Schiffeinzel
from models import Sektion
from models import Teilnehmer
from models import Wettkampf

from fields import MitgliedSearchField
from fields import UnicodeSlugField


def get_startkategorie(steuermann, vorderfahrer):
    if steuermann == vorderfahrer:
        return steuermann
    kat_I = Kategorie.objects.get(name='I')
    kat_II = Kategorie.objects.get(name='II')
    kat_III = Kategorie.objects.get(name='III')
    kat_C = Kategorie.objects.get(name='C')
    kat_D = Kategorie.objects.get(name='D')
    kat_F = Kategorie.objects.get(name='F')
    if steuermann in (kat_I, kat_II) and vorderfahrer in (kat_I, kat_II):
        return kat_II
    if steuermann in (kat_I, kat_II, kat_III) and vorderfahrer in (kat_I, kat_II, kat_III):
        return kat_III
    if steuermann in (kat_III, kat_C, kat_D, kat_F) and vorderfahrer in (kat_III, kat_C, kat_D, kat_F):
        return kat_C
    return None


class WettkampfForm(ModelForm):
    name = UnicodeSlugField(
            help_text=u"Beispiele: 'Fällbaumcup' oder 'Wallbach'")
    zusatz = CharField(
            help_text="Beispiele: 'Bremgarten, 15. Mai 2007' "
                "oder 'Einzelfahren, 17.-18. Juni 2008'",
            widget=TextInput(attrs={'size':'40'}))

    class Meta:
        model = Wettkampf

    def clean(self):
        cleaned_data = self.cleaned_data
        von = cleaned_data.get("von")
        bis = cleaned_data.get("bis")
        name = cleaned_data.get("name")

        if von and bis:
            if bis < von:
                raise ValidationError(u"Von muss älter als bis sein")

        if von and name:
            q = Wettkampf.objects.filter(name=name, von__year=von.year)
            # Wenn ein persistenter Wettkampf editiert wird, muss dieser hier
            # rausgefiltert werden, damit die Validierungsmeldung stimmt.
            q = q.exclude(id=self.instance.id)
            if q.count() > 0:
                raise ValidationError(u"Der Name '%s' ist im Jahr '%d' "
                        "bereits vergeben" % (name, von.year))

        return cleaned_data


class DisziplinForm(ModelForm):
    INITIAL_NAME = u'automatisch-gefüllt'
    name = UnicodeSlugField(
            initial=INITIAL_NAME,
            label='Namen')

    class Meta:
        model = Disziplin

    def __init__(self, wettkampf, *args, **kwargs):
        super(DisziplinForm, self).__init__(*args, **kwargs)
        self.data['wettkampf'] = wettkampf.id
        self.fields['wettkampf'].widget = HiddenInput()

    def clean(self):
        cleaned_data = self.cleaned_data
        name = cleaned_data.get('name')
        if self.instance.id is None and name == self.INITIAL_NAME:
             cleaned_data['name'] = self._default_name()
        q = Disziplin.objects.filter(
                wettkampf=cleaned_data['wettkampf'],
                name=cleaned_data.get('name'))
        # Remove current object from queryset
        q = q.exclude(id=self.instance.id)
        if q.count() > 0:
            # Make sure newly created name is displayed
            self.data['name'] = cleaned_data['name']
            raise ValidationError(
                    u"Für den Wettkampf '%s' ist der Name '%s' bereits vergeben"
                        % (cleaned_data['wettkampf'], cleaned_data['name']))
        return cleaned_data

    def _default_name(self):
        disziplinart = self.cleaned_data['disziplinart']
        default_name = disziplinart.name
        if disziplinart.id == 1: # Einzelfahren
            for k in self.cleaned_data['kategorien']:
                default_name += '-%s' % (k.name,)
        return default_name


class PostenListForm(ModelForm):
    name = UnicodeSlugField(widget=TextInput(attrs={'size':'3'}))

    class Meta:
        model = Posten

    def __init__(self, disziplin, *args, **kwargs):
        super(PostenListForm, self).__init__(*args, **kwargs)
        self.data['disziplin'] = disziplin.id
        self.fields['disziplin'].widget = HiddenInput()
        self.fields['reihenfolge'].required = False
        self.fields["postenart"].queryset = Postenart.objects.filter(
                disziplinarten = disziplin.disziplinart.id
                )

    def clean_name(self):
        cleaned_data = self.cleaned_data
        name = cleaned_data.get('name')
        q = Posten.objects.filter(
                disziplin=cleaned_data.get('disziplin'),
                name=cleaned_data.get('name'))
        # Remove current object from queryset
        q = q.exclude(id=self.instance.id)
        if q.count() > 0:
            raise ValidationError(
                    u"Der Name '%s' ist bereits vergeben" % (name))
        return name

    def clean(self):
        super(ModelForm, self).clean()
        cleaned_data = self.cleaned_data
        disziplin = cleaned_data.get('disziplin')
        reihenfolge = cleaned_data.get('reihenfolge')
        if not reihenfolge:
            cleaned_data['reihenfolge'] = disziplin.posten_set.count() + 1
        return cleaned_data


class PostenEditForm(PostenListForm):
    def __init__(self, disziplin, *args, **kwargs):
        super(PostenEditForm, self).__init__(disziplin, *args, **kwargs)
        self.fields['reihenfolge'].widget = TextInput(attrs={'size':'2'})


class StartlisteFilterForm(Form):
    disziplin = None
    sektion = ModelChoiceField(
            required=False,
            queryset=Sektion.objects.all(),
            )
    startnummern = RegexField(
            regex=re.compile(r'^[-,\d]+$', re.UNICODE),
            required=False,
            widget=TextInput(attrs={'size':'5'}),
            help_text=u"Beispiele: '1-6,9' oder '600-'",
            error_messages={
                'invalid': u"Bitte nur ganze Zahlen, Bindestrich oder Komma eingeben"
                },
            )

    # TODO Nur den Startnummern String parsen, kein Database Lookup:
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
    # Reihenfolge beibehalten. 
    #  (Beispiel: '1,3,2,5' => [('range', [1,3,2,5]))
    #  Wichtig ist hier, dass die Datenbank die Startnummern in zufälliger
    #  Reihenfolge sendet, aber der Benutzer die Nummern in spezifischer
    #  Reihenfolge haben möchte.
    #
    # Example of dynamic or query with Q object:
    #   q = Q( tag__name=first_tag )
    #   for tag in other_tags:
    #       q = q | Q( tag__name=tag )
    #   Model.objects.filter( q )
    #
    def clean_startnummern(self):
        cleaned_data = self.cleaned_data
        startnummern = cleaned_data.get('startnummern')
        if startnummern:
            result=[]
            commas = startnummern.split(',')
            for c in commas:
                if c == '':
                    text = u"Ein Komma ohne Zahl links und rechts ist nicht gültig."
                    raise ValidationError(text)
                dashes = c.split('-')
                if len(dashes) == 1:
                    result.append(c)
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
                        q = Teilnehmer.objects.filter(
                                disziplin=self.disziplin,
                                startnummer__gte=from_nr
                                )
                    elif from_nr == '':
                        q = Teilnehmer.objects.filter(
                                disziplin=self.disziplin,
                                startnummer__lte=until_nr
                                )
                    else:
                        q = Teilnehmer.objects.filter(
                                disziplin=self.disziplin,
                                startnummer__range=dashes
                                )
                    for t in q:
                        result.append(t.startnummer)
            cleaned_data['startnummern_list'] = result

        return startnummern


class StartlisteEntryForm(ModelForm):
    steuermann = MitgliedSearchField(queryset=Mitglied.objects.all())
    vorderfahrer = MitgliedSearchField(queryset=Mitglied.objects.all())

    def __init__(self, disziplin, *args, **kwargs):
        super(StartlisteEntryForm, self).__init__(*args, **kwargs)
        self.data['disziplin'] = disziplin.id
        self.fields['startnummer'].widget = TextInput(attrs={'size':'2'})
        # Folgende Felder werden in clean() gesetzt, deshalb nicht required
        self.fields['sektion'].required = False
        self.fields['kategorie'].required = False
        self.fields['schiffsart'].required = False

    class Meta:
        model = Schiffeinzel

    # TODO super.validate_unique() wird nicht aufgerufen, weil es eine
    # Subklasse ist: Wahrscheinlich ein Fehler in Django
    def clean_startnummer(self):
        cleaned_data = self.cleaned_data
        startnummer = cleaned_data.get('startnummer')
        disziplin = cleaned_data.get('disziplin')
        q = Teilnehmer.objects.filter(
                disziplin=disziplin,
                startnummer=startnummer,
                )
        q = q.exclude(id=self.instance.id)
        if q.count() > 0:
            raise ValidationError(
                    u"Startnummer '%s' ist bereits vergeben" % (startnummer))
        return startnummer

    def _set_data(self, mitglied, field_name):
        if mitglied:
            self.data[field_name] = mitglied.get_edit_text()
        else:
            field = self.fields[field_name]
            if isinstance(field.widget, Select):
                self.data[field_name] = field.queryset[0].id

    #
    # TODO Doppelstarter Info darstellen, falls gleicher Fahrer mit frühere
    # Startnr existiert
    #
    # TODO Doppelstarter Warnung darstellen, falls gleicher Fahrer mit
    # *späterer* Startnr existiert => Eventuell Hilfstabelle führen, welche
    # Startnummernblöcke definiert
    #
    def clean(self):
        super(ModelForm, self).clean()
        cleaned_data = self.cleaned_data
        steuermann = cleaned_data.get('steuermann')
        vorderfahrer = cleaned_data.get('vorderfahrer')
        self._set_data(steuermann, 'steuermann')
        self._set_data(vorderfahrer, 'vorderfahrer')
        if steuermann and vorderfahrer:
            if steuermann == vorderfahrer:
                text = u"Steuermann kann nicht gleichzeitig Vorderfahrer sein"
                raise ValidationError(text)
            if steuermann.sektion != vorderfahrer.sektion:
                # TODO: Als Warnung darstellen, die der Benutzer quittieren muss
                text = u"Steuermann fährt für '%s', Vorderfahrer für '%s'. Soll das Schiff für die Sektion des Steuermann fahren?" % (steuermann.sektion, vorderfahrer.sektion)
                raise ValidationError(text)
            cleaned_data['sektion'] = steuermann.sektion
            steuermann_kat = steuermann.kategorie()
            vorderfahrer_kat = vorderfahrer.kategorie()
            startkategorie = get_startkategorie(steuermann_kat, vorderfahrer_kat)
            if startkategorie is None:
                # TODO: Als Warnung darstellen, die der Benutzer quittieren muss
                text = u"Steuermann hat Kategorie '%s', Vorderfahrer Kategorie '%s'. Das eine unbekannte Kombination. Bitte manuell eine Kategorie wählen." % (steuermann_kat, vorderfahrer_kat)
                raise ValidationError(text)
            cleaned_data['kategorie'] = startkategorie
        return cleaned_data


class SchiffeinzelEditForm(StartlisteEntryForm):

    def __init__(self, disziplin, *args, **kwargs):
        super(SchiffeinzelEditForm, self).__init__(disziplin, *args, **kwargs)
        self.fields['sektion'].required = True
        self.fields['kategorie'].required = True
