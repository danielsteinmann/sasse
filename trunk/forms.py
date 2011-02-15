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
from django.forms.models import BaseModelFormSet

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
from models import Richtzeit
from models import Kranzlimite

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
    return Kategorie.objects.get(
            Q(geschlecht='e') | Q(geschlecht=mitglied.geschlecht),
            Q(alter_von__lte=alter),
            Q(alter_bis__gte=alter)
            )


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

    def anzeigeliste(self):
        sektion = self.cleaned_data.get('sektion')
        startnummern = self.cleaned_data.get('startnummern')
        result = Schiffeinzel.objects.filter(disziplin=self.disziplin)
        if startnummern:
            list = self.fields['startnummern'].startnummern_list
            result = result.filter(startnummer__in=list)
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
        startnummer = cleaned_data.get('startnummer')
        if startnummer:
            q = Schiffeinzel.objects.filter(startnummer=startnummer,
                    disziplin=self.data['disziplin'])
            # Wenn ein persistenter Teilnemer editiert wird, muss dieser hier
            # rausgefiltert werden, damit die Validierungsmeldung stimmt.
            q = q.exclude(id=self.instance.id)
            if q.count() > 0:
                raise ValidationError(u"Die Startnummer '%d' ist bereits "
                        "vergeben" % (startnummer))

        return cleaned_data


class SchiffeinzelListForm(SchiffeinzelEditForm):

    def __init__(self, disziplin, *args, **kwargs):
        super(SchiffeinzelListForm, self).__init__(disziplin, *args, **kwargs)
        self.fields['startnummer'].widget = TextInput(attrs={'size':'3'})
        self.fields['sektion'].widget = HiddenInput()
        # Folgende Felder werden in clean() gesetzt, deshalb nicht required
        self.fields['sektion'].required = False
        self.fields['kategorie'].required = False
        # TODO Gruusig, dass ich dummy Werte wegen der Model-Validierung setzen muss
        self.data['sektion'] = 1
        self.data['kategorie'] = 1

    #
    # TODO Doppelstarter Info darstellen, falls gleicher Fahrer mit frühere
    # Startnr existiert
    #
    # TODO Doppelstarter Warnung darstellen, falls gleicher Fahrer mit
    # *späterer* Startnr existiert => Eventuell Hilfstabelle führen, welche
    # Startnummernblöcke definiert
    #
    # TODO Was passiert, wenn ein Doppelstarter in einer anderen Kategorie
    # passiert. Beispiel:
    #      Steinmann     Kohler   C
    #      Steinmann*    Dux      D
    # 
    # TODO Es gibt der Fall, wo Name/Vorname innerhalb der Sektion zweimal
    # vorkommt (z.B. Schenker Michael). Dropdown Liste mit Jahrgang ergänzen
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

    def clean(self):
        cleaned_data = self.cleaned_data
        startnummern_value = cleaned_data.get('startnummern')
        if startnummern_value and not self.selected_startnummern().count():
            msg = u"Für diesen Filter gibt es keine Startnummern."
            raise ValidationError(msg)
        return cleaned_data

    def selected_startnummern(self, visible=15):
        startnummern = self.cleaned_data.get('startnummern')
        result = Schiffeinzel.objects.filter(disziplin=self.disziplin)
        if startnummern:
            list = self.fields['startnummern'].startnummern_list
            result = result.filter(startnummer__in=list)
        result = result.filter()[:visible]
        return result


class BewertungForm(Form):
    id = IntegerField(required=False, widget=HiddenInput())

    def __init__(self, *args, **kwargs):
        self.posten = kwargs.pop("posten")
        self.bewertungsart = kwargs.pop("bewertungsart")
        self.teilnehmer_id = kwargs.pop("teilnehmer_id")
        super(BewertungForm, self).__init__(*args, **kwargs)
        # Dynamisches Bewertungsfeld einfügen
        if self.bewertungsart.einheit == 'ZEIT':
            wert_field = ZeitInSekundenField()
        else:
            wert_field = PunkteField(self.bewertungsart)
        self.fields['wert'] = wert_field
        # Definiere Initial Value von Bewertungsfeld
        if self.initial.get('id') is None:
            self.initial['wert'] = self.bewertungsart.defaultwert

    def save(self):
        if self.has_changed():
            wert = self.cleaned_data['wert']
            b = Bewertung()
            b.id = self.cleaned_data['id']
            if self.bewertungsart.einheit == 'ZEIT':
                b.zeit = wert
            else:
                b.note = wert
            b.posten_id = self.posten.id
            b.bewertungsart_id = self.bewertungsart.id
            b.teilnehmer_id = self.teilnehmer_id
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
        self.teilnehmer_ids = kwargs.pop("teilnehmer_ids")
        self.extra = len(self.teilnehmer_ids)
        # Mit Hilfe eines einzigen Select (Performance) sich merken, zu
        # welchem Teilnehmer bereits eine Bewertung existiert
        self.bewertung = {}
        ids = self.teilnehmer_ids
        for b in Bewertung.objects.filter(posten=self.posten,
                bewertungsart=self.bewertungsart, teilnehmer__id__in=ids):
            self.bewertung[b.teilnehmer_id] = b
        super(BewertungBaseFormSet, self).__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        initial = {}
        teilnehmer_id = self.teilnehmer_ids[i]
        instance = self.bewertung.get(teilnehmer_id)
        if instance is not None:
            initial['id'] = instance.id
            if instance.bewertungsart.einheit == 'ZEIT':
                initial['wert'] = instance.zeit
            else:
                initial['wert'] = instance.note
        kwargs["initial"] = initial
        kwargs["posten"] = self.posten
        kwargs["bewertungsart"] = self.bewertungsart
        kwargs["teilnehmer_id"] = teilnehmer_id
        return super(BewertungBaseFormSet, self)._construct_form(i, **kwargs)

    def save(self):
        for form in self.forms:
            form.save()


class TeilnehmerForm(Form):
    """
    Hilfsform für TeilnehmerContainerForm.
    """
    id = IntegerField(widget=HiddenInput())
    startnummer = IntegerField(widget=HiddenInput())


class TeilnehmerContainerForm(Form):
    """
    Hiermit kann man die Liste der Startnummern auf dem Postenblatt darstellen
    (GET) respektive auszulesen (POST).
    
    Ich habe kein ModelFormSet von Django verwendet, weil es dies nicht
    erlaubt, das queryset aus dem POST Request zu rekonstruieren.
    """
    PREFIX = 'stnr-%d'
    total = IntegerField(widget=HiddenInput())

    def __init__(self, teilnehmer_ids=None, *args, **kwargs):
        self.teilnehmer_ids = teilnehmer_ids
        super(TeilnehmerContainerForm, self).__init__(*args, **kwargs)
        if self.teilnehmer_ids and self.data:
            msg = u"Entweder teilnehmer_ids oder data, aber nicht beide"
            raise AssertionError(msg)
        if self.teilnehmer_ids:
            self.initial['total'] = len(self.teilnehmer_ids)
        else:
            if not self.is_valid():
                msg = u"Das hidden Feld 'total' nicht im Template vorhanden"
                raise ValidationError(msg)

    def teilnehmer_forms(self):
        """
        Wandelt die beim Konstruktor angegebene Startliste in eine Liste von
        TeilnehmerForm um.
        """
        result = []
        for i, teilnehmer_id in enumerate(self.teilnehmer_ids):
            form = TeilnehmerForm(prefix=self.PREFIX % i)
            form.initial['teilnehmer'] = teilnehmer_id
            result.append(form)
        return result

    def exctract_teilnehmer_ids(self):
        """
        Wandelt die beim Konstruktor angegebenen POST Parameter in eine Liste
        von Teilnehmer IDs um.
        """
        result = []
        count = self.cleaned_data['total']
        for i in range(0, count):
            form = TeilnehmerForm(self.data, prefix=self.PREFIX % i)
            form.is_valid()
            id = form.cleaned_data['teilnehmer']
            result.append(id)
        return result


def create_postenblatt_formsets(posten, teilnehmer_ids, data=None):
    """
    Hiermit kann man die Liste der Startnummern auf dem Postenblatt darstellen
    (GET) respektive auszulesen (POST).
    
    Ich habe kein ModelFormSet von Django verwendet, weil es dies nicht
    erlaubt, das queryset aus dem POST Request zu rekonstruieren.
    """
    result = []
    FormSet = formset_factory(form=BewertungForm, formset=BewertungBaseFormSet)
    for art in Bewertungsart.objects.filter(postenart=posten.postenart,
            editierbar=True):
        formset = FormSet(posten=posten, bewertungsart=art, prefix=art.name,
                teilnehmer_ids=teilnehmer_ids, data=data)
        result.append(formset)
    return result


class RichtzeitForm(ModelForm):
    class Meta:
        model = Richtzeit

    def __init__(self, posten, *args, **kwargs):
        try:
            kwargs['instance'] = Richtzeit.objects.get(posten=posten)
        except Richtzeit.DoesNotExist:
            pass
        super(RichtzeitForm, self).__init__(*args, **kwargs)
        self.fields['zeit'] = ZeitInSekundenField()
        self.fields['posten'].widget = HiddenInput()
        self.initial['posten'] = posten.id


class KranzlimiteForm(Form):
    kat_id = IntegerField(widget=HiddenInput())
    kat_name = CharField(widget=TextInput(attrs={'size': '2', 'readonly': 'True'}))
    kl_id = IntegerField(required=False, widget=HiddenInput())
    kl_wert = DecimalField(required=False)
