# -*- coding: utf-8 -*-

import datetime
import re
from decimal import Decimal

from django.db.models import Q
from django.forms import CharField
from django.forms import DecimalField
from django.forms import IntegerField
from django.forms import TimeField
from django.forms import Form
from django.forms import HiddenInput
from django.forms import ModelChoiceField
from django.forms import ModelForm
from django.forms import RegexField
from django.forms import Select
from django.forms import TextInput
from django.forms import ValidationError

from django.forms.formsets import BaseFormSet
from django.forms.formsets import formset_factory

from models import Bewertung
from models import Bewertungsart
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


def get_startkategorie(a, b):
    if a == b:
        return a
    kat_I = Kategorie.objects.get(name='I')
    kat_II = Kategorie.objects.get(name='II')
    kat_III = Kategorie.objects.get(name='III')
    kat_C = Kategorie.objects.get(name='C')
    kat_D = Kategorie.objects.get(name='D')
    kat_F = Kategorie.objects.get(name='F')
    if a in (kat_I, kat_II) and b in (kat_I, kat_II):
        return kat_II
    if a in (kat_I, kat_II, kat_III) and b in (kat_I, kat_II, kat_III):
        return kat_III
    if a in (kat_III, kat_C, kat_D, kat_F) and b in (kat_III, kat_C, kat_D, kat_F):
        return kat_C
    return None

def get_kategorie(aktuelles_jahr, mitglied):
    alter = aktuelles_jahr - mitglied.geburtsdatum.year
    try:
        return Kategorie.objects.get(
                geschlecht=mitglied.geschlecht,
                alter_von__lte=alter, alter_bis__gte=alter)
    except Kategorie.DoesNotExist:
        # Passiert, wenn das Mitglied eine Frau ist, welche das Alter für die
        # Kategorie 'F' noch nicht erreicht hat.
        return Kategorie.objects.get(
                geschlecht='m',
                alter_von__lte=alter, alter_bis__gte=alter)


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
            name = self._default_name()
            cleaned_data['name'] = name
            # Zeige generierten Name falls ein ValidationError auftritt
            self.data['name'] = name
        super(DisziplinForm, self).clean()
        return cleaned_data

    def _default_name(self):
        disziplinart = self.cleaned_data['disziplinart']
        default_name = disziplinart.name
        if disziplinart.id == 1: # Einzelfahren
            for k in self.cleaned_data['kategorien']:
                default_name += '-%s' % (k.name,)
        return default_name


class PostenListForm(ModelForm):
    name = UnicodeSlugField(widget=TextInput(attrs={'size':'3'}), label='Name')

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


class SchiffeinzelFilterForm(Form):
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

    def __init__(self, disziplin, *args, **kwargs):
        super(SchiffeinzelFilterForm, self).__init__(*args, **kwargs)
        self.disziplin = disziplin

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

    def anzeigeliste(self, visible=10):
        sektion = self.cleaned_data.get('sektion')
        startnummern = self.cleaned_data.get('startnummern_list')
        result = Schiffeinzel.objects.filter(disziplin=self.disziplin)
        if startnummern is None and sektion is None:
            # Performance: Nur die letzten n Eintraege darstellen
            last = result.count()
            almostlast = last - visible
            if almostlast > 0:
                result = result.filter()[almostlast:last]
        if startnummern is not None:
            result = result.filter(startnummer__in=startnummern)
        if sektion is not None:
            result = result.filter(sektion=sektion)
        return result

    def naechste_nummer(self, startliste):
        """Nächste Startnummer ist die zuletzt dargestellte Nummer plus 1"""
        anzahl_sichtbar = startliste.count()
        if anzahl_sichtbar == 0:
            result = 1
        else:
            letzter_sichtbar = startliste[anzahl_sichtbar - 1]
            result = letzter_sichtbar.startnummer + 1
        return result


class SchiffeinzelEditForm(ModelForm):
    steuermann = MitgliedSearchField(queryset=Mitglied.objects.all())
    vorderfahrer = MitgliedSearchField(queryset=Mitglied.objects.all())

    class Meta:
        model = Schiffeinzel

    def __init__(self, disziplin, *args, **kwargs):
        super(SchiffeinzelEditForm, self).__init__(*args, **kwargs)
        self.data['disziplin'] = disziplin.id
        self.fields['schiffsart'].required = False

    def set_display_value(self, mitglied, field_name):
        if mitglied:
            self.data[field_name] = mitglied.get_edit_text()
        else:
            field = self.fields[field_name]
            if isinstance(field.widget, Select):
                self.data[field_name] = field.queryset[0].id

    def clean(self):
        super(ModelForm, self).clean()
        cleaned_data = self.cleaned_data
        steuermann = cleaned_data.get('steuermann')
        vorderfahrer = cleaned_data.get('vorderfahrer')
        self.set_display_value(steuermann, 'steuermann')
        self.set_display_value(vorderfahrer, 'vorderfahrer')
        return cleaned_data


class SchiffeinzelListForm(SchiffeinzelEditForm):

    def __init__(self, disziplin, *args, **kwargs):
        super(SchiffeinzelListForm, self).__init__(disziplin, *args, **kwargs)
        self.fields['startnummer'].widget = TextInput(attrs={'size':'2'})
        self.fields['sektion'].widget = HiddenInput()
        # Folgende Felder werden in clean() gesetzt, deshalb nicht required
        self.fields['sektion'].required = False
        self.fields['kategorie'].required = False

    #
    # TODO Doppelstarter Info darstellen, falls gleicher Fahrer mit frühere
    # Startnr existiert
    #
    # TODO Doppelstarter Warnung darstellen, falls gleicher Fahrer mit
    # *späterer* Startnr existiert => Eventuell Hilfstabelle führen, welche
    # Startnummernblöcke definiert
    #
    def clean(self):
        super(SchiffeinzelListForm, self).clean()
        cleaned_data = self.cleaned_data
        disziplin = cleaned_data.get('disziplin')
        steuermann = cleaned_data.get('steuermann')
        vorderfahrer = cleaned_data.get('vorderfahrer')
        sektion = cleaned_data.get('sektion')
        if steuermann and vorderfahrer:
            if steuermann == vorderfahrer:
                text = u"Steuermann kann nicht gleichzeitig Vorderfahrer sein"
                raise ValidationError(text)
            if steuermann.sektion != vorderfahrer.sektion and not sektion:
                text = u"Steuermann fährt für '%s', Vorderfahrer für '%s'. Das Schiff wird für '%s' fahren" % (steuermann.sektion, vorderfahrer.sektion, steuermann.sektion)
                self.data['sektion'] = steuermann.sektion.id
                raise ValidationError(text)
            cleaned_data['sektion'] = steuermann.sektion
            jahr = disziplin.wettkampf.jahr()
            steuermann_kat = get_kategorie(jahr, steuermann)
            vorderfahrer_kat = get_kategorie(jahr, vorderfahrer)
            startkategorie = get_startkategorie(steuermann_kat, vorderfahrer_kat)
            if startkategorie is None:
                text = u"Steuermann hat Kategorie '%s', Vorderfahrer Kategorie '%s'. Das ist eine unerlaubte Kombination." % (steuermann_kat, vorderfahrer_kat)
                raise ValidationError(text)
            cleaned_data['kategorie'] = startkategorie
        return cleaned_data


# TODO: Problem mit Abzug lösen, wo man z.B. 3 Punkte Abzug eingibt, aber auf
# der Datenbank eine 7 speichern muss (10 ist das Maximum, 3 ist der Abzug).
# Das gilt für die meisten Posten, ausser die Anmeldung.
class BewertungForm(Form):
    id = IntegerField(required=False, widget=HiddenInput())
    teilnehmer = IntegerField(widget=HiddenInput())
    wert = DecimalField(max_digits=4, decimal_places=2,
            widget=TextInput(attrs={'size': '1'}))

    def __init__(self, *args, **kwargs):
        self.posten = kwargs.pop("posten")
        self.bewertungsart = kwargs.pop("bewertungsart")
        super(BewertungForm, self).__init__(*args, **kwargs)
        wert = self.bewertungsart.defaultwert
        if self.bewertungsart.einheit == 'ZEIT':
            # TODO Spezialfeld einführen
            self.fields['wert'].widget = TextInput(attrs={'size': '2'})
        else:
            if self.initial.get('id') is not None:
                wert = self.initial['wert']
                if wert != 0:
                    # Vermeide Darstellung von '-0'
                    wert = wert * self.bewertungsart.signum
        self.initial['wert'] = wert

    def clean_wert(self):
        wert = self.cleaned_data.get('wert')
        if self.bewertungsart.einheit == 'PUNKT':
            # TODO: Richtiger Wertebereich überprüfen
            if wert % 1 not in (0, Decimal('0.5')):
                msg = u'Nur ganze Zahlen oder Vielfaches von 0.5 erlaubt'
                raise ValidationError(msg)
            # Wert wird wenn nötig als negative Zahl gespeichert, damit man
            # einfacher mit SQL sum() arbeiten kann.
            return wert * self.bewertungsart.signum
        return wert

    def has_changed(self):
        """
        Mit diesem Trick liefert form.cleaned_data.get('wert') *immer* einen
        Wert zurück, auch wenn der Benutzer nichts ändert und somit den
        Default Wert speichern möchte.

        Das ist nötig für die Erstellung der Rangliste, weil für jeden
        Teilnehmer/Posten/Bewertungsart ein Record in Bewertung stehen muss.
        """
        if self.initial.get('id') is None:
            return True
        else:
            return super(BewertungForm, self).has_changed()

    def save(self):
        if self.has_changed():
            b = Bewertung()
            b.id = self.cleaned_data['id']
            b.teilnehmer_id = self.cleaned_data['teilnehmer']
            b.wert = self.cleaned_data['wert']
            b.posten_id = self.posten.id
            b.bewertungsart_id = self.bewertungsart.id
            b.save()
            return b


class BewertungBaseFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        self.posten = kwargs.pop("posten")
        self.bewertungsart = kwargs.pop("bewertungsart")
        self.startliste = kwargs.pop("startliste")
        self.extra = len(self.startliste)
        # Mit Hilfe eines einzigen Select (Performance) sich merken, zu
        # welchem Teilnehmer bereits eine Bewertung existiert
        self.bewertung = {}
        ids = [t.id for t in self.startliste]
        for b in Bewertung.objects.filter(posten=self.posten,
                bewertungsart=self.bewertungsart, teilnehmer__id__in=ids):
            self.bewertung[b.teilnehmer.id] = b
        super(BewertungBaseFormSet, self).__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        kwargs["posten"] = self.posten
        kwargs["bewertungsart"] = self.bewertungsart
        initial = {}
        teilnehmer = self.startliste[i]
        instance = self.bewertung.get(teilnehmer.id)
        if instance is not None:
            initial['id'] = instance.id
            initial['wert'] = instance.wert
        initial['teilnehmer'] = teilnehmer.id
        kwargs["initial"] = initial
        return super(BewertungBaseFormSet, self)._construct_form(i, **kwargs)

    def save(self):
        for form in self.forms:
            form.save()


def create_postenblatt_formsets(posten, startliste=None, data=None):
    FormSet = formset_factory(form=BewertungForm, formset=BewertungBaseFormSet)
    result = []
    for art in Bewertungsart.objects.filter(postenart=posten.postenart):
        formset = FormSet(posten=posten, bewertungsart=art, prefix=art.name,
                startliste=startliste, data=data)
        result.append(formset)
    return result

