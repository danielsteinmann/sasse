# -*- coding: utf-8 -*-

import datetime
import re
from decimal import Decimal

from django.db.models import Q
from django.forms import BooleanField
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
from models import GESCHLECHT_ART

from fields import MitgliedSearchField
from fields import UnicodeSlugField
from fields import ZeitInSekundenField
from fields import PunkteField
from fields import StartnummernSelectionField

from queries import create_mitglieder_nummer

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
        # Dieses Flag ermöglicht es, auf der Startlisten Seite nach einer
        # Sektion zu filtern, für die noch keine Schiffe existieren, um dann
        # dann mit der Eingabe zu beginnen. Ohne dieses Flag würde eine
        # Fehlermeldung erscheinen, womit eine Eingabe nicht möglich wäre.
        self.sektion_check = kwargs.pop('sektion_check', True)
        super(SchiffeinzelFilterForm, self).__init__(*args, **kwargs)
        self.fields['startnummern'] = StartnummernSelectionField(disziplin)
        self.disziplin = disziplin

    def clean(self):
        schiffe = self.cleaned_data.get('startnummern')
        if schiffe:
            sektion = self.cleaned_data.get('sektion')
            if sektion:
                schiffe = schiffe.filter(sektion=sektion)
                if self.sektion_check and not schiffe:
                    text = u"Keine Schiffe mit diesen Suchkritierien gefunden."
                    raise ValidationError(text)
        self.schiffe = schiffe
        return self.cleaned_data

    def naechste_nummer(self):
        """
        Nächste Startnummer ist die zuletzt dargestellte Nummer plus 1
        """
        anzahl_sichtbar = self.schiffe.count()
        if anzahl_sichtbar == 0:
            result = 1
        else:
            letzter_sichtbar = self.schiffe[anzahl_sichtbar - 1]
            result = letzter_sichtbar.startnummer + 1
        return result

    def selected_startnummern(self, visible=15):
        schiffe = self.schiffe.filter()[:visible]
        return schiffe


class SchiffeinzelEditForm(ModelForm):
    steuermann = MitgliedSearchField(queryset=Mitglied.objects.all())
    vorderfahrer = MitgliedSearchField(queryset=Mitglied.objects.all())

    class Meta:
        model = Schiffeinzel

    def __init__(self, disziplin, *args, **kwargs):
        super(SchiffeinzelEditForm, self).__init__(*args, **kwargs)
        self.data['disziplin'] = disziplin.id
        self.fields['startnummer'].widget.attrs['size'] = 3
        self.fields['sektion'].empty_label = None
        self.fields['kategorie'].empty_label = None
        self.initial['steuermann'] = self.fields['steuermann'].value_for_form(self.instance.steuermann)
        self.initial['vorderfahrer'] = self.fields['vorderfahrer'].value_for_form(self.instance.vorderfahrer)

    def clean(self):
        super(SchiffeinzelEditForm, self).clean()
        for name in ('steuermann', 'vorderfahrer'):
            mitglied = self.cleaned_data.get(name)
            self.data[name] = self.fields[name].value_for_form(mitglied)
        return self.cleaned_data


class SchiffeinzelListForm(Form):
    startnummer = IntegerField()
    steuermann = MitgliedSearchField(queryset=Mitglied.objects.all())
    steuermann_neu = BooleanField(required=False, label="Neues Mitglied erfassen")
    vorderfahrer = MitgliedSearchField(queryset=Mitglied.objects.all())
    vorderfahrer_neu = BooleanField(required=False, label="Neues Mitglied erfassen")
    # Folgende Felder werden in clean() gesetzt, deshalb nicht required
    sektion = ModelChoiceField(queryset=Sektion.objects.all(), widget=HiddenInput(), required=False)
    kategorie = ModelChoiceField(queryset=Kategorie.objects.all(), widget=HiddenInput(), required=False)

    def __init__(self, disziplin, *args, **kwargs):
        self.disziplin = disziplin
        self.filter_sektion = kwargs.pop('filter_sektion', None)
        super(SchiffeinzelListForm, self).__init__(*args, **kwargs)
        self.fields['startnummer'].widget.attrs['size'] = 3
        # Damit für den Normalfall effizient mit Tab navigieren kann
        self.fields['steuermann_neu'].widget.attrs['tabindex'] = '-1'
        self.fields['vorderfahrer_neu'].widget.attrs['tabindex'] = '-1'

    def steuermann_neu_form(self):
        return self._mitglied_neu_form('steuermann', 'steuermann_neu')

    def vorderfahrer_neu_form(self):
        return self._mitglied_neu_form('vorderfahrer', 'vorderfahrer_neu')

    def _mitglied_neu_form(self, position, flag_field):
        if not self.data.has_key(flag_field):
            # Falls Benutzer ein neues Mitglied eingeben will, ein leeres
            # Formular ohne Validierungsfehler anzeigen. Falls Sektion im
            # Suchfilter gesetzt wurde, die Sektion schon vorselektieren.
            initial = {}
            if self.filter_sektion:
                initial['sektion'] = self.filter_sektion.id
            form = MitgliedForm(prefix=position, initial=initial)
        else:
            form = MitgliedForm(prefix=position, data=self.data)
            if form.is_valid():
                mitglied = form.save()
                # Neues Mitglied im Suchfeld darstellen
                self.data[position] = self.fields[position].value_for_form(mitglied)
                # Felder zur Erfassung des neuen Mitgliedes ausblenden
                self.data[flag_field] = False
        return form

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
        for name in ('steuermann', 'vorderfahrer'):
            mitglied = self.cleaned_data.get(name)
            self.data[name] = self.fields[name].value_for_form(mitglied)
        steuermann = self.cleaned_data.get('steuermann')
        vorderfahrer = self.cleaned_data.get('vorderfahrer')
        if not (steuermann and vorderfahrer):
            return self.cleaned_data
        if steuermann == vorderfahrer:
            text = u"Steuermann kann nicht gleichzeitig Vorderfahrer sein"
            raise ValidationError(text)
        # Sektion
        sektion = self.cleaned_data.get('sektion')
        if sektion is None:
            sektion = steuermann.sektion
            if steuermann.sektion != vorderfahrer.sektion:
                text = u"Steuermann fährt für '%s', Vorderfahrer für '%s'. Bitte Vorschlag bestätigen oder andere Sektion wählen." % (steuermann.sektion, vorderfahrer.sektion)
                self.data['sektion'] = steuermann.sektion.id
                self.fields['sektion'] = ModelChoiceField(queryset=Sektion.objects.all(), empty_label=None)
                raise ValidationError(text)
        if self.filter_sektion and self.filter_sektion != sektion:
            text = u"Schiff soll für '%s' fahren, aber oben ist '%s' vorselektiert. Bitte vorgeschlagene Sektion bestätigen oder einen anderen Steuermann auswählen." % (sektion, self.filter_sektion)
            self.data['sektion'] = self.filter_sektion.id
            self.fields['sektion'] = ModelChoiceField(queryset=Sektion.objects.all(), empty_label=None)
            raise ValidationError(text)
        # Kategorie
        kategorie = self.cleaned_data.get('kategorie')
        if kategorie is None:
            jahr = self.disziplin.wettkampf.jahr()
            steuermann_kat = get_kategorie(jahr, steuermann)
            vorderfahrer_kat = get_kategorie(jahr, vorderfahrer)
            kategorie = get_startkategorie(steuermann_kat, vorderfahrer_kat)
            if kategorie is None:
                text = u"Steuermann hat Kategorie '%s', Vorderfahrer Kategorie '%s'. Das ist eine unbekannte Kombination; bitte auswählen." % (steuermann_kat, vorderfahrer_kat)
                self.fields['kategorie'] = ModelChoiceField(queryset=Kategorie.objects.all(), empty_label=None)
                raise ValidationError(text)
        # Unique Startnummer
        self.instance = Schiffeinzel(
                disziplin=self.disziplin,
                startnummer=self.cleaned_data.get('startnummer'),
                steuermann=steuermann,
                vorderfahrer=vorderfahrer,
                sektion=sektion,
                kategorie=kategorie,
                )
        self.instance.validate_unique()
        return self.cleaned_data

    def save(self):
        self.instance.save()
        return self.instance


class TeilnehmerForm(Form):
    id = IntegerField(widget=HiddenInput())
    startnummer = IntegerField(widget=HiddenInput())


class BewertungForm(Form):
    id = IntegerField(required=False, widget=HiddenInput())

    def __init__(self, *args, **kwargs):
        self.posten = kwargs.pop("posten")
        self.bewertungsart = kwargs.pop("bewertungsart")
        self.teilnehmer_id = kwargs.pop("teilnehmer_id")
        self.is_checksum = kwargs.get('initial', {}).get("is_checksum", False)
        super(BewertungForm, self).__init__(*args, **kwargs)
        # Dynamisches Bewertungsfeld einfügen
        if self.is_checksum:
            wert_field = DecimalField(required=False)
        elif self.bewertungsart.einheit == 'ZEIT':
            wert_field = ZeitInSekundenField()
        else:
            wert_field = PunkteField(self.bewertungsart)
        self.fields['wert'] = wert_field

    def save(self):
        if not self.is_checksum and self.has_changed():
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


def create_bewertung_initials(posten, bewertungsart, teilnehmer_ids):
    # Mit Hilfe eines einzigen Select (Performance) sich merken, zu
    # welchem Teilnehmer bereits eine Bewertung existiert
    bewertung_by_tid = {}
    for b in Bewertung.objects.filter(posten=posten,
            bewertungsart=bewertungsart, teilnehmer__id__in=teilnehmer_ids):
        bewertung_by_tid[b.teilnehmer_id] = b
    # Nun pro Teilnehmer die Initials für die BewertungForm definieren
    initials = []
    checksum = 0
    for tid in teilnehmer_ids:
        values = {}
        instance = bewertung_by_tid.get(tid)
        if instance is None:
            values['wert'] = bewertungsart.defaultwert
        else:
            values['id'] = instance.id
            if instance.bewertungsart.einheit == 'ZEIT':
                values['wert'] = instance.zeit
            else:
                values['wert'] = instance.note
        initials.append(values)
        checksum += values['wert']
    # Und nun noch den Initialwert für die Checksumme
    initials.append({'wert': checksum, 'is_checksum': True})
    return initials


class BewertungBaseFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        self.posten = kwargs.pop("posten")
        self.bewertungsart = kwargs.pop("bewertungsart")
        self.teilnehmer_ids = kwargs.pop("teilnehmer_ids")
        super(BewertungBaseFormSet, self).__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        kwargs["posten"] = self.posten
        kwargs["bewertungsart"] = self.bewertungsart
        if self.initial and self.initial[i].has_key('is_checksum'):
            kwargs["teilnehmer_id"] = -1
        else:
            kwargs["teilnehmer_id"] = self.teilnehmer_ids[i]
        return super(BewertungBaseFormSet, self)._construct_form(i, **kwargs)

    def clean(self):
        if any(self.errors):
            return
        # Das letzte Form ist für die Checksumme
        checksum_eingabe = self.forms[-1].cleaned_data['wert']
        if checksum_eingabe is None:
            # Falls Checksumme nicht eingegeben wurde, kann man sich die
            # Checksummenvalidierung sparen
            return
        # Berechne Checksumme (ohne das letzte Form)
        checksum_calc = 0
        for form in self.forms[:-1]:
            checksum_calc += form.cleaned_data['wert']
        if checksum_eingabe != checksum_calc:
            msg = u"Die Zahl %s erwartet" % (checksum_calc,)
            # Hänge Fehlermeldung an das Checksummenfeld
            self.forms[-1]._errors['wert'] = self.error_class([msg])

    def save(self):
        for form in self.forms:
            form.save()


def create_postenblatt_formsets(posten, teilnehmer_ids, data=None):
    """
    Hiermit kann man die Liste der Startnummern auf dem Postenblatt darstellen
    (GET) respektive auszulesen (POST).
    
    Ich habe kein ModelFormSet von Django verwendet, weil es dies nicht
    erlaubt, das queryset aus dem POST Request zu rekonstruieren.
    """
    result = []
    FormSet = formset_factory(form=BewertungForm, formset=BewertungBaseFormSet, extra=0)
    for art in Bewertungsart.objects.filter(postenart=posten.postenart,
            editierbar=True):
        initials = create_bewertung_initials(posten, art, teilnehmer_ids)
        formset = FormSet(posten=posten, bewertungsart=art, prefix=art.name,
                teilnehmer_ids=teilnehmer_ids, initial=initials, data=data)
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


class MitgliedForm(Form):
    name = CharField()
    vorname = CharField()
    jahrgang = IntegerField()
    sektion = ModelChoiceField(queryset=Sektion.objects.all())
    geschlecht = ChoiceField(choices=GESCHLECHT_ART, initial='m')

    def __init__(self, *args, **kwargs):
        super(MitgliedForm, self).__init__(*args, **kwargs)
        today = datetime.date.today()
        max_jahrgang = today.year - 1
        min_jahrgang = today.year - 100
        self.fields['jahrgang'] = IntegerField(max_value=max_jahrgang, min_value=min_jahrgang)

    def save(self):
        m = Mitglied()
        m.nummer = create_mitglieder_nummer()
        m.name = self.cleaned_data['name']
        m.vorname = self.cleaned_data['vorname']
        m.geburtsdatum = datetime.date(self.cleaned_data['jahrgang'], 1, 1)
        m.sektion = self.cleaned_data['sektion']
        m.geschlecht = self.cleaned_data['geschlecht']
        m.save()
        return m

