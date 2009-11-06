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
from django.forms import ChoiceField
from django.forms import RadioSelect
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
from fields import ZeitInSekundenField
from fields import PunkteField
from fields import StartnummernSelectionField


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
    sektion = ModelChoiceField(
            required=False,
            queryset=Sektion.objects.all(),
            )

    def __init__(self, disziplin, *args, **kwargs):
        super(SchiffeinzelFilterForm, self).__init__(*args, **kwargs)
        self.fields['startnummern'] = StartnummernSelectionField(disziplin)
        self.disziplin = disziplin

    def anzeigeliste(self, visible=10):
        sektion = self.cleaned_data.get('sektion')
        startnummern = self.fields['startnummern'].startnummern_list
        result = Schiffeinzel.objects.filter(disziplin=self.disziplin)
        if not startnummern and not sektion:
            # Nur die letzten n Eintraege darstellen
            last = result.count()
            almostlast = last - visible
            if almostlast > 0:
                result = result.filter()[almostlast:last]
        if startnummern:
            result = result.filter(startnummer__in=startnummern)
        if sektion:
            result = result.filter(sektion=sektion)
        return result

    def naechste_nummer(self, startliste):
        """
        Nächste Startnummer ist die zuletzt dargestellte Nummer plus 1
        """
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


class PostenblattFilterForm(Form):
    def __init__(self, disziplin, *args, **kwargs):
        self.disziplin = disziplin
        super(PostenblattFilterForm, self).__init__(*args, **kwargs)
        self.fields['startnummern'] = StartnummernSelectionField(disziplin)

    def selected_startnummern(self, visible=15):
        # TODO: Falls keine Startnummern eingegeben, suche ersten Teilnehmer
        # ohne Bewertungen für den aktuellen Posten.
        nummern = self.fields['startnummern'].startnummern_list
        result = Schiffeinzel.objects.filter(disziplin=self.disziplin)
        if nummern:
            result = result.filter(startnummer__in=nummern)
        result = result.filter()[:visible]
        return result

    def next_posten(self, current_posten):
        result = None
        try:
            next = self.disziplin.posten_set.filter(
                    reihenfolge__gt=current_posten.reihenfolge)
            result = next.filter()[0]
        except IndexError:
            # current_posten ist der letzte Posten der Postenliste
            pass
        return result


# TODO: Problem mit Abzug lösen, wo man z.B. 3 Punkte Abzug eingibt, aber auf
# der Datenbank eine 7 speichern muss (10 ist das Maximum, 3 ist der Abzug).
# Das gilt für die meisten Posten, ausser die Anmeldung.
class BewertungForm(Form):
    id = IntegerField(required=False, widget=HiddenInput())
    teilnehmer = IntegerField(widget=HiddenInput())

    def __init__(self, *args, **kwargs):
        self.posten = kwargs.pop("posten")
        self.bewertungsart = kwargs.pop("bewertungsart")
        super(BewertungForm, self).__init__(*args, **kwargs)
        # Definiere Typ von Bewertungsfeld
        if self.bewertungsart.einheit == 'ZEIT':
            wert_field = ZeitInSekundenField()
        else:
            wert_field = PunkteField(self.bewertungsart)
        # Definiere Initial Value von Bewertungsfeld
        if self.initial.get('id') is None:
            wert_initial = self.bewertungsart.defaultwert
        else:
            # Wert wird wenn nötig als negative Zahl gespeichert, damit man
            # einfacher mit SQL sum() arbeiten kann (siehe save()). Darum
            # hier das Vorzeichen wieder kehren.
            wert_initial = self.initial['wert']
            if wert_initial != 0:
                # Vermeide Darstellung von '-0'
                wert_initial = wert_initial * self.bewertungsart.signum
        # Dynamisches Bewertungsfeld einfügen
        self.fields['wert'] = wert_field
        self.initial['wert'] = wert_initial

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
            # Wert wird wenn nötig als negative Zahl gespeichert, damit man
            # einfacher mit SQL sum() arbeiten kann.
            b.wert = self.cleaned_data['wert'] * self.bewertungsart.signum
            b.posten_id = self.posten.id
            b.bewertungsart_id = self.bewertungsart.id
            b.save()
            return b


class BewertungBaseFormSet(BaseFormSet):
    """
    Formset für eine Liste von Startnummern.  Das Postenblatt besteht aus 1-n
    solchen Formsets.  Gibt man 'einzelfahren/postenblatt/' ein, also keine
    konkreten Parameter, dann wird der erste Posten mit den ersten 15
    Startnummern gezeigt.
    """
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

