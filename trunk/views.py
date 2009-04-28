# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django import forms
from django.forms import ModelForm
from django.forms import Form
from django.forms import ValidationError
from django.shortcuts import render_to_response

from models import Postenart
from models import Mitglied
from models import Sektion

from models import Wettkampf
from models import Disziplin
from models import Posten
from models import Teilnehmer
from models import Schiffeinzel


def wettkaempfe_get(request):
    assert request.method == 'GET'
    wettkaempfe = Wettkampf.objects.all()
    return render_to_response('wettkampf_list.html',
            {'wettkaempfe': wettkaempfe})

def wettkaempfe_add(request):
    if request.method == 'POST':
        return wettkaempfe_post(request)
    assert request.method == 'GET'
    form = WettkampfForm()
    return render_to_response('wettkampf_add.html',
            {'form': form})

def wettkaempfe_post(request):
    assert request.method == 'POST'
    form = WettkampfForm(request.POST)
    if form.is_valid():
        form.save()
        jahr = form.cleaned_data['von'].year
        name = form.cleaned_data['name']
        return HttpResponseRedirect(reverse(wettkampf_get, args=[jahr, name]))
    return render_to_response('wettkampf_add.html', {'form': form,})

def wettkaempfe_by_year(request, jahr):
    assert request.method == 'GET'
    wettkaempfe = Wettkampf.objects.filter(von__year=jahr)
    return render_to_response('wettkampf_list.html',
            {'wettkaempfe': wettkaempfe, 'year': jahr})

def wettkampf_get(request, jahr, wettkampf):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = w.disziplin_set.all()
    return render_to_response('wettkampf.html',
            {'wettkampf': w, 'disziplinen': d})

def wettkampf_update(request, jahr, wettkampf):
    if request.method == 'POST':
        return wettkampf_put(request, jahr, wettkampf)
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = w.disziplin_set.all()
    form = WettkampfForm(instance=w)
    return render_to_response('wettkampf_update.html',
            {'wettkampf': w, 'disziplinen': d, 'form': form})

def wettkampf_put(request, jahr, wettkampf):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    form = WettkampfForm(request.POST, instance=w)
    if form.is_valid():
        form.save()
        jahr = form.cleaned_data['von'].year
        name = form.cleaned_data['name']
        return HttpResponseRedirect(reverse(wettkampf_get, args=[jahr, name]))
    d = w.disziplin_set.all()
    return render_to_response('wettkampf_update.html',
            {'wettkampf': w, 'disziplinen': d, 'form': form})

def wettkampf_delete_confirm(request, jahr, wettkampf):
    if request.method == 'POST':
        return wettkampf_delete(request, jahr, wettkampf)
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    return render_to_response('wettkampf_delete.html', {'wettkampf': w})

def wettkampf_delete(request, jahr, wettkampf):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    w.delete()
    return HttpResponseRedirect(reverse(wettkaempfe_get))

def disziplinen_add(request, jahr, wettkampf):
    if request.method == 'POST':
        return disziplinen_post(request, jahr, wettkampf)
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    form = DisziplinForm(initial={'wettkampf': w.id})
    return render_to_response('disziplin_add.html',
            {'form': form, 'wettkampf': w})

def disziplinen_post(request, jahr, wettkampf):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    form = DisziplinForm(request.POST.copy())
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(wettkampf_get, args=[jahr, wettkampf]))
    return render_to_response('disziplin_add.html',
            {'form': form, 'wettkampf': w})

def disziplin_get(request, jahr, wettkampf, disziplin):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    return render_to_response('disziplin.html', {'wettkampf': w, 'disziplin': d})

def disziplin_update(request, jahr, wettkampf, disziplin):
    if request.method == 'POST':
        return disziplin_put(request, jahr, wettkampf, disziplin)
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    form = DisziplinForm(instance=d)
    return render_to_response('disziplin_update.html',
            {'form': form, 'wettkampf': w, 'disziplin': d})

def disziplin_put(request, jahr, wettkampf, disziplin):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    form = DisziplinForm(request.POST.copy(), instance=d)
    if form.is_valid():
        form.save()
        disziplin = form.cleaned_data['name']
        return HttpResponseRedirect(reverse(disziplin_get,
            args=[jahr, wettkampf, disziplin]))
    return render_to_response('disziplin_update.html',
            {'form': form, 'wettkampf': w, 'disziplin': d})

def disziplin_delete_confirm(request, jahr, wettkampf, disziplin):
    if request.method == 'POST':
        return disziplin_delete(request, jahr, wettkampf, disziplin)
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    return render_to_response('disziplin_delete.html', {'wettkampf': w, 'disziplin': d})

def disziplin_delete(request, jahr, wettkampf, disziplin):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    d.delete()
    return HttpResponseRedirect(reverse(wettkampf_get, args=[jahr, wettkampf]))

def posten_list(request, jahr, wettkampf, disziplin):
    if request.method == 'POST':
        return posten_post(request, jahr, wettkampf, disziplin)
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    form = PostenListForm(initial={'disziplin': d.id,
        'reihenfolge': d.posten_set.count() + 1, })
    form.fields["postenart"].queryset = Postenart.objects.filter(disziplinarten = d.disziplinart.id)
    return render_to_response('posten.html',
        {'wettkampf': w, 'disziplin': d, 'posten': d.posten_set.all(),
            'form': form, })

def posten_post(request, jahr, wettkampf, disziplin):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    form = PostenListForm(request.POST)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(posten_list, args=[jahr, wettkampf, disziplin]))
    form.fields["postenart"].queryset = Postenart.objects.filter(disziplinarten = d.disziplinart.id)
    return render_to_response('posten.html',
        {'wettkampf': w, 'disziplin': d, 'posten': d.posten_set.all(),
          'form': form, })

def posten_get(request, jahr, wettkampf, disziplin, posten):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    p = Posten.objects.get(disziplin=d, name=posten)
    return render_to_response('posten_get.html',
        {'wettkampf': w, 'disziplin': d, 'posten': p, })

def posten_update(request, jahr, wettkampf, disziplin, posten):
    if request.method == 'POST':
        return posten_put(request, jahr, wettkampf, disziplin, posten)
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    p = Posten.objects.get(disziplin=d, name=posten)
    form = PostenEditForm(instance=p)
    form.fields["postenart"].queryset = Postenart.objects.filter(disziplinarten = d.disziplinart.id)
    return render_to_response('posten_update.html',
            {'form': form, 'wettkampf': w, 'disziplin': d, 'posten': p, })

def posten_put(request, jahr, wettkampf, disziplin, posten):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    p = Posten.objects.get(disziplin=d, name=posten)
    form = PostenEditForm(request.POST.copy(), instance=p)
    if form.is_valid():
        form.save()
        posten = form.cleaned_data['name']
        return HttpResponseRedirect(reverse(posten_list,
            args=[jahr, wettkampf, disziplin]))
    form.fields["postenart"].queryset = Postenart.objects.filter(disziplinarten = d.disziplinart.id)
    return render_to_response('posten_update.html',
            {'form': form, 'wettkampf': w, 'disziplin': d, 'posten': p, })

def posten_delete_confirm(request, jahr, wettkampf, disziplin, posten):
    if request.method == 'POST':
        return posten_delete(request, jahr, wettkampf, disziplin, posten)
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    p = Posten.objects.get(disziplin=d, name=posten)
    return render_to_response('posten_delete.html',
            {'wettkampf': w, 'disziplin': d, 'posten': p, })

def posten_delete(request, jahr, wettkampf, disziplin, posten):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    p = Posten.objects.get(disziplin=d, name=posten)
    p.delete()
    return HttpResponseRedirect(reverse(posten_list,
        args=[jahr, wettkampf, disziplin]))

# TODO Nur für Einzelfahren gültig
def startliste(request, jahr, wettkampf, disziplin):
    if request.method == 'POST':
        return startliste_post(request, jahr, wettkampf, disziplin)
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    searchform = StartlisteFilterForm(request.GET)
    searchform.disziplin = d
    if searchform.is_valid():
        sektion = searchform.cleaned_data.get('sektion')
        startnummern = searchform.cleaned_data.get('startnummern_list')
        s = Schiffeinzel.objects.filter(disziplin=d)
        if startnummern is not None:
            s = s.filter(startnummer__in=startnummern)
        if sektion is not None:
            s = s.filter(sektion=sektion)
        # Nächste Startnummer ist die zuletzt dargestellte Nummer plus 1
        anzahl_total = d.teilnehmer_set.count()
        if anzahl_total == 0:
            naechste_nummer = 1
        else:
            anzahl_sichtbar = s.count()
            if anzahl_sichtbar == 0:
                naechste_nummer = None
            else:
                letzter_sichtbar = s[anzahl_sichtbar - 1]
                naechste_nummer = letzter_sichtbar.startnummer + 1
        form = StartlisteEntryForm(d, initial={'startnummer': naechste_nummer})
    else:
        s = []
        form = None
    return render_to_response('startliste.html', {
        'wettkampf': w, 'disziplin': d, 'searchform': searchform,
        'startliste': s, 'form': form,
        })

def startliste_post(request, jahr, wettkampf, disziplin):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    s = Schiffeinzel.objects.filter(disziplin=d)
    form = StartlisteEntryForm(d, request.POST.copy())
    if form.is_valid():
        form.save()
        url = reverse(startliste, args=[jahr, wettkampf, disziplin])
        query = request.META.get('QUERY_STRING')
        if query:
            url = "%s?%s" % (url, query)
        return HttpResponseRedirect(url)
    searchform = StartlisteFilterForm(request.GET)
    searchform.disziplin = d
    if searchform.is_valid():
        sektion = searchform.cleaned_data.get('sektion')
        startnummern = searchform.cleaned_data.get('startnummern_list')
        if startnummern is not None:
            s = s.filter(startnummer__in=startnummern)
        if sektion is not None:
            s = s.filter(sektion=sektion)
    return render_to_response('startliste.html',
            {'wettkampf': w, 'disziplin': d, 'startliste': s, 'form': form,
                'searchform': searchform})

def teilnehmer_get(request, jahr, wettkampf, disziplin, startnummer):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    t = Schiffeinzel.objects.get(disziplin=d, startnummer=startnummer)
    return render_to_response('schiffeinzel.html',
            {'wettkampf': w, 'disziplin': d, 'teilnehmer': t})

def teilnehmer_update(request, jahr, wettkampf, disziplin, startnummer):
    if request.method == 'POST':
        return teilnehmer_put(request, jahr, wettkampf, disziplin, startnummer)
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    t = Schiffeinzel.objects.get(disziplin=d, startnummer=startnummer)
    form = SchiffeinzelEditForm(d, initial={
        'steuermann': t.steuermann.nummer,
        'vorderfahrer': t.vorderfahrer.nummer,
        },
        instance=t)
    return render_to_response('schiffeinzel_update.html',
            {'wettkampf': w, 'disziplin': d, 'form': form, 'teilnehmer': t})

def teilnehmer_put(request, jahr, wettkampf, disziplin, startnummer):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    t = Schiffeinzel.objects.get(disziplin=d, startnummer=startnummer)
    form = SchiffeinzelEditForm(d, request.POST.copy(), instance=t)
    if form.is_valid():
        form.save()
        startnummer = form.cleaned_data['startnummer']
        url = reverse(teilnehmer_get, args=[jahr, wettkampf, disziplin, startnummer])
        return HttpResponseRedirect(url)
    return render_to_response('schiffeinzel_update.html',
            {'wettkampf': w, 'disziplin': d, 'form': form, 'teilnehmer': t})

def teilnehmer_delete_confirm(request, jahr, wettkampf, disziplin, startnummer):
    if request.method == 'POST':
        return teilnehmer_delete(request, jahr, wettkampf, disziplin, startnummer)
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    t = Schiffeinzel.objects.get(disziplin=d, startnummer=startnummer)
    return render_to_response('schiffeinzel_delete.html',
            {'wettkampf': w, 'disziplin': d, 'teilnehmer': t})

def teilnehmer_delete(request, jahr, wettkampf, disziplin, startnummer):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    t = Schiffeinzel.objects.get(disziplin=d, startnummer=startnummer)
    t.delete()
    url = reverse(startliste, args=[jahr, wettkampf, disziplin])
    return HttpResponseRedirect(url)

import re
name_re = re.compile(r'^[-\w]+$', re.UNICODE)
invalid_name_message = \
u"Bitte nur Buchstaben und Ziffern (inklusive Bindestrich) eingeben"

class WettkampfForm(ModelForm):
    name = forms.RegexField(regex=name_re,
            help_text=u"Beispiele: 'Fällbaumcup' oder 'Wallbach'",
            error_messages={'invalid': invalid_name_message})
    zusatz = forms.CharField(
            help_text="Beispiele: 'Bremgarten, 15. Mai 2007' "
                "oder 'Einzelfahren, 17.-18. Juni 2008'",
            widget=forms.TextInput(attrs={'size':'40'}))


    class Meta:
        model = Wettkampf


    def clean(self):
        cleaned_data = self.cleaned_data
        von = cleaned_data.get("von")
        bis = cleaned_data.get("bis")
        name = cleaned_data.get("name")

        if von and bis:
            if bis < von:
                raise ValidationError(u"Von muss Ã¤lter als bis sein")

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
    wettkampf = forms.ModelChoiceField(
            queryset=Wettkampf.objects.all(),
            widget=forms.HiddenInput)
    name = forms.RegexField(regex=name_re,
            initial=INITIAL_NAME,
            error_messages={'invalid': invalid_name_message})

    class Meta:
        model = Disziplin

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
    disziplin = forms.ModelChoiceField(
            queryset=Disziplin.objects.all(),
            widget=forms.HiddenInput)
    name = forms.RegexField(regex=name_re,
            error_messages={'invalid': invalid_name_message},
            widget=forms.TextInput(attrs={'size':'3'}))
    reihenfolge = forms.DecimalField(widget=forms.HiddenInput)


    class Meta:
        model = Posten

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


class PostenEditForm(PostenListForm):
    reihenfolge = forms.DecimalField(
            widget=forms.TextInput(attrs={'size':'2'}))


class StartlisteFilterForm(Form):
    disziplin = None
    sektion = forms.ModelChoiceField(
            required=False,
            queryset=Sektion.objects.all(),
            )
    startnummern = forms.RegexField(
            regex=re.compile(r'^[-,\d]+$', re.UNICODE),
            required=False,
            widget=forms.TextInput(attrs={'size':'5'}),
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


class MitgliedSearchField(forms.ModelChoiceField):

    def __init__(self, *args, **kwargs):
        kwargs['widget'] = kwargs.pop('widget', forms.widgets.TextInput)
        super(MitgliedSearchField, self).__init__(*args, **kwargs)

    #
    # TODO Doppelstarter Info darstellen, falls gleicher Fahrer mit frühere
    # Startnr existiert
    #
    # TODO Doppelstarter Warnung darstellen, falls gleicher Fahrer mit
    # *späterer* Startnr existiert => Eventuell Hilfstabelle führen, welche
    # Startnummernblöcke definiert
    #
    def clean(self, value):
        if self.required and not value:
            raise ValidationError(self.error_messages['required'])
        try:
            nummer = int(value)
            q = Mitglied.objects.filter(nummer__contains=value)
        except ValueError:
            items = value.split()
            if len(items) == 1:
                q = Mitglied.objects.filter(name__icontains=items[0])
            elif len(items) == 2:
                q = Mitglied.objects.filter(
                        name__icontains=items[0],
                        vorname__icontains=items[1])
        if q.count() == 0:
            text = u"Mitglied '%s' nicht gefunden. Bitte 'Name' oder 'Mitgliedernummer' eingeben" % (value,)
            raise ValidationError(text)
        elif q.count() > 1:
            text = u"Mitglied '%s' ist nicht eindeutig (%d mal gefunden)" % (value, q.count())
            raise ValidationError(text)
        return q[0]


class StartlisteEntryForm(ModelForm):
    steuermann = MitgliedSearchField(queryset=Teilnehmer.objects.all())
    vorderfahrer = MitgliedSearchField(queryset=Teilnehmer.objects.all())

    def __init__(self, disziplin, *args, **kwargs):
        super(StartlisteEntryForm, self).__init__(*args, **kwargs)
        self.data['disziplin'] = disziplin.id
        self.fields['startnummer'].widget = forms.TextInput(attrs={'size':'2'})
        # Folgende Felder werden in clean() gesetzt, deshalb nicht required
        self.fields['sektion'].required = False
        self.fields['kategorie'].required = False
        self.fields['schiffsart'].required = False

    class Meta:
        model = Schiffeinzel

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

    def clean(self):
        super(ModelForm, self).clean()
        cleaned_data = self.cleaned_data
        steuermann = cleaned_data.get('steuermann')
        vorderfahrer = cleaned_data.get('vorderfahrer')
        if steuermann and vorderfahrer:
            if steuermann.sektion != vorderfahrer.sektion:
                # TODO: Dies als Warnung darstellen, die der Benutzer quittieren muss
                text = u"Steuermann fährt für '%s', Vorderfahrer für '%s'. Soll das Schiff für die Sektion des Steuermann fahren?" % (steuermann.sektion, vorderfahrer.sektion)
                raise ValidationError(text)
            if steuermann == vorderfahrer:
                text = u"Steuermann kann nicht gleichzeitig Vorderfahrer sein"
                raise ValidationError(text)
            cleaned_data['sektion'] = steuermann.sektion
            # TODO: Korrekte Startkategorie ermittelt und ValidationError darstellen,
            # falls Kategorie nicht ermittelt werden kann
            cleaned_data['kategorie'] = steuermann.kategorie()
        return cleaned_data


class SchiffeinzelEditForm(StartlisteEntryForm):

    def __init__(self, disziplin, *args, **kwargs):
        super(SchiffeinzelEditForm, self).__init__(disziplin, *args, **kwargs)
        self.fields['sektion'].required = True
        self.fields['kategorie'].required = True

