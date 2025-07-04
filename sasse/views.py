# -*- coding: utf-8 -*-

import datetime
from openpyxl import Workbook

from django.core.paginator import Paginator
from django.db import transaction
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.http import HttpResponse
from django.template import RequestContext
from django.forms.formsets import formset_factory, all_valid
from django.utils.encoding import smart_str
from django.shortcuts import render
from django.contrib.auth.decorators import permission_required

from .models import Wettkampf
from .models import Disziplin
from .models import Disziplinart
from .models import Posten
from .models import Teilnehmer
from .models import Schiffeinzel
from .models import Richtzeit
from .models import Sektion
from .models import Sektionsfahrengruppe
from .models import Kranzlimite
from .models import Mitglied
from .models import Schiffsektion
from .models import SektionsfahrenKranzlimiten
from .models import SpezialwettkaempfeKranzlimite
from .models import Schwimmer
from .models import Einzelschnuerer
from .models import Schnuergruppe
from .models import Bootfaehrengruppe
from .models import Kategorie
from .models import Generationenpaar

from .forms import DisziplinForm
from .forms import PostenEditForm
from .forms import PostenListForm
from .forms import SchiffeinzelEditForm
from .forms import SchiffeinzelListForm
from .forms import SchiffeinzelFilterForm
from .forms import TeilnehmerForm
from .forms import WettkampfForm
from .forms import create_postenblatt_formsets
from .forms import RichtzeitForm
from .forms import KranzlimiteForm
from .forms import MitgliedForm
from .forms import StartlisteUploadFileForm
from .forms import GruppeForm
from .forms import GruppeFilterForm
from .forms import SchiffsektionForm
from .forms import SektionsfahrenGruppeAbzugForm
from .forms import SektionsfahrenKranzlimitenForm
from .forms import SpezialwettkaempfeKranzlimiteForm
from .forms import SchwimmerForm
from .forms import SchwimmerUpdateForm
from .forms import EinzelschnuererForm
from .forms import EinzelschnuererUpdateForm
from .forms import SchnuergruppeForm
from .forms import SchnuergruppeUpdateForm
from .forms import BootfaehrengruppeForm
from .forms import BootfaehrengruppeUpdateForm
from .forms import GenerationenpaarForm
from .forms import GenerationenpaarUpdateForm
from .forms import EinzelfahrenZeitUploadFileForm
from .forms import SektionsfahrenZeitUploadForm
from .forms import EinzelfahrenNotenUploadFileForm

from .queries import read_topzeiten
from .queries import read_notenliste
from .queries import read_notenblatt
from .queries import read_kranzlimite
from .queries import read_kranzlimiten
from .queries import read_kranzlimite_pro_kategorie
from .queries import read_rangliste
from .queries import sort_rangliste
from .queries import read_startende_kategorien
from .queries import read_anzahl_wettkaempfer
from .queries import read_doppelstarter
from .queries import read_sektionsfahren_rangliste
from .queries import read_sektionsfahren_rangliste_gruppe
from .queries import read_sektionsfahren_rangliste_schiff
from .queries import read_sektionsfahren_notenblatt_gruppe
from .queries import read_sektionsfahren_topzeiten
from .queries import read_schwimmen_gestartete_kategorien
from .queries import read_einzelschnueren_gestartete_kategorien
from .queries import read_gruppenschnueren_gestartete_kategorien
from .queries import read_bootfaehrenbau_gestartete_kategorien
from .queries import read_beste_fahrerpaare
from .queries import read_beste_saisonpaare
from .queries import read_einzelfahren_null_zeiten
from .queries import read_sektionsfahren_null_zeiten
from .queries import read_beste_generationenpaare
from .queries import read_aelteste_fahrerpaare

from .reports import create_rangliste_doctemplate
from .reports import create_rangliste_flowables
from .reports import create_rangliste_header
from .reports import create_bestzeiten_flowables
from .reports import create_notenblatt_doctemplate
from .reports import create_notenblatt_flowables
from .reports import create_startliste_doctemplate
from .reports import create_startliste_flowables
from .reports import create_notenliste_doctemplate
from .reports import create_notenliste_flowables
from .reports import create_sektionsfahren_rangliste_flowables
from .reports import create_sektionsfahren_notenblatt_doctemplate
from .reports import create_sektionsfahren_notenblatt_flowables
from .reports import create_sektionsfahren_notenblatt_gruppe_doctemplate
from .reports import create_sektionsfahren_notenblatt_gruppe_flowables
from .reports import create_schwimmen_rangliste_flowables
from .reports import create_einzelschnueren_rangliste_flowables
from .reports import create_gruppenschnueren_rangliste_flowables
from .reports import create_bootfaehrenbau_rangliste_flowables
from .reports import create_beste_saisonpaare_doctemplate
from .reports import create_beste_saisonpaare_flowables

from . import eai_startliste
from . import eai_zeiten
from . import eai_noten

def wettkaempfe_get(request):
    assert request.method == 'GET'
    wettkaempfe = Wettkampf.objects.all()
    return render(request, 'wettkampf_list.html',
            {'wettkaempfe': wettkaempfe})

@permission_required('sasse.add_wettkampf')
def wettkaempfe_add(request):
    if request.method == 'POST':
        return wettkaempfe_post(request)
    assert request.method == 'GET'
    form = WettkampfForm()
    return render(request, 'wettkampf_add.html', {'form': form})

@permission_required('sasse.add_wettkampf')
def wettkaempfe_post(request):
    assert request.method == 'POST'
    form = WettkampfForm(request.POST)
    if form.is_valid():
        w = form.save()
        url = reverse(wettkampf_get, args=[w.jahr(), w.name])
        return HttpResponseRedirect(url)
    return render(request, 'wettkampf_add.html', {'form': form,})

def wettkaempfe_by_year(request, jahr):
    assert request.method == 'GET'
    wettkaempfe = Wettkampf.objects.filter(von__year=jahr)
    return render(request, 'wettkampf_list.html',
            {'wettkaempfe': wettkaempfe, 'year': jahr})

def wettkampf_get(request, jahr, wettkampf):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = w.disziplin_set.all()
    return render(request, 'wettkampf.html',
            {'wettkampf': w, 'disziplinen': d})

@permission_required('sasse.change_wettkampf')
def wettkampf_update(request, jahr, wettkampf):
    if request.method == 'POST':
        return wettkampf_put(request, jahr, wettkampf)
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = w.disziplin_set.all()
    form = WettkampfForm(instance=w)
    return render(request, 'wettkampf_update.html',
            {'wettkampf': w, 'disziplinen': d, 'form': form})

@permission_required('sasse.change_wettkampf')
def wettkampf_put(request, jahr, wettkampf):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    form = WettkampfForm(request.POST, instance=w)
    if form.is_valid():
        w = form.save()
        url = reverse(wettkampf_get, args=[w.jahr(), w.name])
        return HttpResponseRedirect(url)
    d = w.disziplin_set.all()
    return render(request, 'wettkampf_update.html',
            {'wettkampf': w, 'disziplinen': d, 'form': form})

@permission_required('sasse.delete_wettkampf')
def wettkampf_delete_confirm(request, jahr, wettkampf):
    if request.method == 'POST':
        return wettkampf_delete(request, jahr, wettkampf)
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    return render(request, 'wettkampf_delete.html', {'wettkampf': w})

@permission_required('sasse.delete_wettkampf')
def wettkampf_delete(request, jahr, wettkampf):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    w.delete()
    return HttpResponseRedirect(reverse(wettkaempfe_get))

@permission_required('sasse.add_disziplin')
def disziplinen_add(request, jahr, wettkampf):
    if request.method == 'POST':
        return disziplinen_post(request, jahr, wettkampf)
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    form = DisziplinForm(w)
    return render(request, 'disziplin_add.html',
            {'form': form, 'wettkampf': w})

@permission_required('sasse.add_disziplin')
def disziplinen_post(request, jahr, wettkampf):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    form = DisziplinForm(w, request.POST.copy())
    if form.is_valid():
        form.save()
        url = reverse(wettkampf_get, args=[jahr, wettkampf])
        return HttpResponseRedirect(url)
    return render(request, 'disziplin_add.html',
            {'form': form, 'wettkampf': w})

def disziplin_get(request, jahr, wettkampf, disziplin):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    return render(request, "einzelfahren.html", {'wettkampf': w,
        'disziplin': d})

@permission_required('sasse.change_disziplin')
def disziplin_update(request, jahr, wettkampf, disziplin):
    if request.method == 'POST':
        return disziplin_put(request, jahr, wettkampf, disziplin)
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    form = DisziplinForm(w, instance=d)
    return render(request, 'disziplin_update.html',
            {'form': form, 'wettkampf': w, 'disziplin': d})

@permission_required('sasse.change_disziplin')
def disziplin_put(request, jahr, wettkampf, disziplin):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    form = DisziplinForm(w, request.POST.copy(), instance=d)
    if form.is_valid():
        d = form.save()
        url = reverse(disziplin_get, args=[jahr, wettkampf, d.name])
        return HttpResponseRedirect(url)
    return render(request, 'disziplin_update.html',
            {'form': form, 'wettkampf': w, 'disziplin': d})

@permission_required('sasse.delete_disziplin')
def disziplin_delete_confirm(request, jahr, wettkampf, disziplin):
    if request.method == 'POST':
        return disziplin_delete(request, jahr, wettkampf, disziplin)
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    return render(request, 'disziplin_delete.html',
            {'wettkampf': w, 'disziplin': d})

@permission_required('sasse.delete_disziplin')
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
    form = PostenListForm(d)
    return render(request, 'posten.html',
        {'wettkampf': w, 'disziplin': d, 'posten': d.posten_set.all(),
            'form': form, })

@permission_required('sasse.add_posten')
def posten_post(request, jahr, wettkampf, disziplin):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    form = PostenListForm(d, request.POST.copy())
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(posten_list, args=[jahr, wettkampf, disziplin]))
    return render(request, 'posten.html',
        {'wettkampf': w, 'disziplin': d, 'posten': d.posten_set.all(),
          'form': form, })

def posten_get(request, jahr, wettkampf, disziplin, posten):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    p = Posten.objects.get(disziplin=d, name=posten)
    return render(request, 'posten_get.html',
            {'wettkampf': w, 'disziplin': d, 'posten': p, 'base_disziplin': 'base_sektionsfahren.html'})

@permission_required('sasse.change_posten')
def posten_update(request, jahr, wettkampf, disziplin, posten):
    if request.method == 'POST':
        return posten_put(request, jahr, wettkampf, disziplin, posten)
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    p = Posten.objects.get(disziplin=d, name=posten)
    form = PostenEditForm(d, instance=p)
    return render(request, 'posten_update.html',
            {'form': form, 'wettkampf': w, 'disziplin': d, 'posten': p, })

@permission_required('sasse.change_posten')
def posten_put(request, jahr, wettkampf, disziplin, posten):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    p = Posten.objects.get(disziplin=d, name=posten)
    form = PostenEditForm(d, request.POST.copy(), instance=p)
    if form.is_valid():
        form.save()
        posten = form.cleaned_data['name']
        return HttpResponseRedirect(reverse(posten_list,
            args=[jahr, wettkampf, disziplin]))
    return render(request, 'posten_update.html',
            {'form': form, 'wettkampf': w, 'disziplin': d, 'posten': p, })

@permission_required('sasse.delete_posten')
def posten_delete_confirm(request, jahr, wettkampf, disziplin, posten):
    if request.method == 'POST':
        return posten_delete(request, jahr, wettkampf, disziplin, posten)
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    p = Posten.objects.get(disziplin=d, name=posten)
    return render(request, 'posten_delete.html',
            {'wettkampf': w, 'disziplin': d, 'posten': p, })

@permission_required('sasse.delete_posten')
def posten_delete(request, jahr, wettkampf, disziplin, posten):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    p = Posten.objects.get(disziplin=d, name=posten)
    p.delete()
    return HttpResponseRedirect(reverse(posten_list,
        args=[jahr, wettkampf, disziplin]))

def startliste(request, jahr, wettkampf, disziplin):
    if request.method == 'POST':
        return startliste_post(request, jahr, wettkampf, disziplin)
    d = Disziplin.objects.select_related().get(
            name=disziplin,
            wettkampf__name=wettkampf,
            wettkampf__von__year=jahr)
    if d.disziplinart.name == "Einzelfahren":
        return startliste_einzelfahren(request, jahr, wettkampf, disziplin)
    else:
        raise Http404("Startliste für %s noch nicht implementiert"
                % d.disziplinart)

def startliste_post(request, jahr, wettkampf, disziplin):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    if d.disziplinart == Disziplinart.objects.get(name="Einzelfahren"):
        return startliste_einzelfahren_post(request, jahr, wettkampf, disziplin)
    else:
        raise Http404("Mutieren der Startliste für %s noch nicht implementiert"
                % d.disziplinart)

def startliste_einzelfahren(request, jahr, wettkampf, disziplin):
    assert request.method == 'GET'
    d = Disziplin.objects.select_related().get(
            name=disziplin,
            wettkampf__name=wettkampf,
            wettkampf__von__year=jahr)
    w = d.wettkampf
    s = []
    entryform = None
    steuermann_neu_form = None
    vorderfahrer_neu_form = None
    searchform = SchiffeinzelFilterForm(d, request.GET, sektion_check=False)
    if searchform.is_valid():
        s = searchform.schiffe.select_related()
        nummer = request.GET.get('startnummer')
        if not nummer:
            nummer = searchform.naechste_nummer()
        initial = {}
        initial['startnummer'] = nummer
        initial['steuermann'] = request.GET.get('steuermann')
        initial['vorderfahrer'] = request.GET.get('vorderfahrer')
        sektion = searchform.cleaned_data['sektion']
        entryform = SchiffeinzelListForm(d, initial=initial, filter_sektion=sektion)
        steuermann_neu_form = entryform.steuermann_neu_form()
        vorderfahrer_neu_form = entryform.vorderfahrer_neu_form()
    paginator = Paginator(s, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, 'startliste_einzelfahren.html', { 'wettkampf': w,
        'disziplin': d, 'searchform': searchform, 'page_obj': page_obj, 'form': entryform,
        'steuermann_neu_form': steuermann_neu_form,
        'vorderfahrer_neu_form': vorderfahrer_neu_form},
        )

def startliste_einzelfahren_pdf(request, jahr, wettkampf, disziplin):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    searchform = SchiffeinzelFilterForm(d, request.GET)
    searchform.is_valid()
    schiffe = searchform.schiffe.select_related()
    doc = create_startliste_doctemplate(w, d)
    flowables = create_startliste_flowables(schiffe)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = smart_str('filename=startliste')
    doc.build(flowables, filename=response)
    return response

@permission_required('sasse.add_schiffeinzel')
def startliste_einzelfahren_post(request, jahr, wettkampf, disziplin):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    searchform = SchiffeinzelFilterForm(d, request.GET, sektion_check=False)
    searchform.is_valid()
    sektion = searchform.cleaned_data['sektion']
    data = request.POST.copy()
    entryform = SchiffeinzelListForm(d, data=data, filter_sektion=sektion)
    steuermann_neu_form = entryform.steuermann_neu_form()
    vorderfahrer_neu_form = entryform.vorderfahrer_neu_form()
    if entryform.is_valid():
        entryform.save()
        url = reverse(startliste, args=[jahr, wettkampf, disziplin])
        query = request.META.get('QUERY_STRING')
        if query:
            url = "%s?%s" % (url, query)
        return HttpResponseRedirect(url)
    paginator = Paginator(searchform.schiffe, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, 'startliste_einzelfahren.html', {
        'wettkampf': w, 'disziplin': d, 'searchform': searchform,
        'page_obj': page_obj, 'form': entryform,
        'steuermann_neu_form': steuermann_neu_form,
        'vorderfahrer_neu_form': vorderfahrer_neu_form})

def teilnehmer_get(request, jahr, wettkampf, disziplin, startnummer):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    t = Schiffeinzel.objects.get(disziplin=d, startnummer=startnummer)
    return render(request, 'schiffeinzel.html', {'wettkampf': w,
        'disziplin': d, 'teilnehmer': t})

@permission_required('sasse.change_schiffeinzel')
def teilnehmer_update(request, jahr, wettkampf, disziplin, startnummer):
    if request.method == 'POST':
        return teilnehmer_put(request, jahr, wettkampf, disziplin, startnummer)
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    t = Schiffeinzel.objects.get(disziplin=d, startnummer=startnummer)
    form = SchiffeinzelEditForm(d, instance=t)
    return render(request, 'schiffeinzel_update.html',
            {'wettkampf': w, 'disziplin': d, 'form': form, 'teilnehmer': t})

@permission_required('sasse.change_schiffeinzel')
def teilnehmer_put(request, jahr, wettkampf, disziplin, startnummer):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    t = Schiffeinzel.objects.get(disziplin=d, startnummer=startnummer)
    form = SchiffeinzelEditForm(d, request.POST.copy(), instance=t)
    if form.is_valid():
        form.save()
        startnummer = form.cleaned_data['startnummer']
        args = [jahr, wettkampf, disziplin, startnummer]
        url = reverse(teilnehmer_get, args=args)
        return HttpResponseRedirect(url)
    return render(request, 'schiffeinzel_update.html',
            {'wettkampf': w, 'disziplin': d, 'form': form, 'teilnehmer': t})

@permission_required('sasse.delete_schiffeinzel')
def teilnehmer_delete_confirm(request, jahr, wettkampf, disziplin, startnummer):
    if request.method == 'POST':
        return teilnehmer_delete(request, jahr, wettkampf, disziplin, startnummer)
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    t = Schiffeinzel.objects.get(disziplin=d, startnummer=startnummer)
    return render(request, 'schiffeinzel_delete.html',
            {'wettkampf': w, 'disziplin': d, 'teilnehmer': t})

@permission_required('sasse.delete_schiffeinzel')
def teilnehmer_delete(request, jahr, wettkampf, disziplin, startnummer):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    t = Schiffeinzel.objects.get(disziplin=d, startnummer=startnummer)
    t.delete()
    url = reverse(startliste, args=[jahr, wettkampf, disziplin])
    return HttpResponseRedirect(url)

def bewertungen(request, jahr, wettkampf, disziplin):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    if d.posten_set.count() == 0:
        raise Http404("Es sind noch keine Posten definiert")
    p = d.posten_set.all()[0]
    url = reverse(postenblatt, args=[jahr, wettkampf, disziplin, p.name])
    return HttpResponseRedirect(url)

def get_postenblatt_filter_form(disziplin):
    if disziplin.disziplinart.name == "Einzelfahren":
        return SchiffeinzelFilterForm
    else:
        return GruppeFilterForm

def postenblatt(request, jahr, wettkampf, disziplin, posten):
    assert request.method == 'GET'
    p = Posten.objects.select_related().get(
            name=posten,
            disziplin__name=disziplin,
            disziplin__wettkampf__name=wettkampf,
            disziplin__wettkampf__von__year=jahr)
    d = p.disziplin
    w = d.wettkampf
    query = request.META.get('QUERY_STRING')
    orientation = get_orientation(p, request)
    header_row = []
    data_rows = []
    filter_form_class = get_postenblatt_filter_form(d)
    filterform = filter_form_class(d, request.GET)
    if filterform.is_valid():
        startnummern = filterform.selected_startnummern(visible=15)
        teilnehmer_ids = [t.id for t in startnummern]
        sets = create_postenblatt_formsets(p, teilnehmer_ids)
        header_row, data_rows = create_postenblatt_table(startnummern, sets, orientation)
    return render(request, 'postenblatt.html', {'wettkampf': w, 'disziplin':
        d, 'posten': p, 'filterform': filterform, 'header_row': header_row,
        'data_rows': data_rows, 'query': query,})

@permission_required('sasse.change_bewertung')
def postenblatt_update(request, jahr, wettkampf, disziplin, posten):
    if request.method == 'POST':
        return postenblatt_post(request, jahr, wettkampf, disziplin, posten)
    assert request.method == 'GET'
    p = Posten.objects.select_related().get(
            name=posten,
            disziplin__name=disziplin,
            disziplin__wettkampf__name=wettkampf,
            disziplin__wettkampf__von__year=jahr)
    d = p.disziplin
    w = d.wettkampf
    header_row = []
    data_rows = []
    teilnehmer_formset = []
    sets = []
    p_next_name = None
    filter_identifier = None
    filter_form_class = get_postenblatt_filter_form(d)
    filterform = filter_form_class(d, request.GET)
    if filterform.is_valid():
        startnummern = filterform.selected_startnummern(visible=15)
        TeilnehmerFormSet = formset_factory(TeilnehmerForm, extra=0)
        initial = [{'id': t.id, 'startnummer': t.startnummer} for t in startnummern]
        teilnehmer_formset = TeilnehmerFormSet(initial=initial, prefix='stnr')
        teilnehmer_ids = [t.id for t in startnummern]
        sets = create_postenblatt_formsets(p, teilnehmer_ids)
        orientation = get_orientation(p, request)
        header_row, data_rows = create_postenblatt_table(startnummern, sets, orientation)
        if filterform.cleaned_data.get('gruppe'):
            filter_identifier = filterform.instance.name
        if filterform.cleaned_data.get('sektion'):
            filter_identifier = filterform.cleaned_data.get('sektion')
        p_next_list = list(d.posten_set.filter(reihenfolge__gt=p.reihenfolge))
        if p_next_list:
            p_next_name = p_next_list[0].name
    return render(request, "postenblatt_update.html", {'wettkampf': w,
        'disziplin': d, 'posten': p, 'teilnehmer_formset': teilnehmer_formset,
        'formset': sets, 'header_row': header_row, 'data_rows': data_rows,
        'posten_next_name': p_next_name, 'filter_identifier': filter_identifier})

@permission_required('sasse.change_bewertung')
@transaction.atomic
def postenblatt_post(request, jahr, wettkampf, disziplin, posten):
    assert request.method == 'POST'
    p = Posten.objects.select_related().get(
            name=posten,
            disziplin__name=disziplin,
            disziplin__wettkampf__name=wettkampf,
            disziplin__wettkampf__von__year=jahr)
    d = p.disziplin
    w = d.wettkampf
    filter_identifier = request.POST.get('filter_identifier')
    p_next_name = request.POST.get('posten_next_name')
    TeilnehmerFormSet = formset_factory(TeilnehmerForm)
    teilnehmer_formset = TeilnehmerFormSet(data=request.POST, prefix='stnr')
    if not teilnehmer_formset.is_valid():
        # Sollte nicht passieren
        raise Exception("%s" % teilnehmer_formset.errors)
    teilnehmer_ids = [f.cleaned_data['id'] for f in teilnehmer_formset.forms]
    sets = create_postenblatt_formsets(p, teilnehmer_ids, data=request.POST)
    if all_valid(sets):
        for formset in sets:
            formset.save()
        view = postenblatt
        if 'save_and_next' in request.POST:
            posten = p_next_name
            view = postenblatt_update
        elif 'save_and_finish' in request.POST:
            # Wir waren auf letztem Posten => Zurück zur Postenblattwahl
            posten = d.posten_set.all()[0].name
            view = postenblatt
        url = reverse(view, args=[jahr, wettkampf, disziplin, posten])
        query = request.META.get('QUERY_STRING')
        if query:
            url = "%s?%s" % (url, query)
        return HttpResponseRedirect(url)
    orientation = get_orientation(p, request)
    startnummern = [f.cleaned_data['startnummer'] for f in teilnehmer_formset.forms]
    header_row, data_rows = create_postenblatt_table(startnummern, sets, orientation)
    return render(request, 'postenblatt_update.html', {'wettkampf': w,
        'disziplin': d, 'posten': p, 'teilnehmer_formset': teilnehmer_formset,
        'formset': sets, 'header_row': header_row, 'data_rows': data_rows,
        'posten_next_name': p_next_name, 'filter_identifier': filter_identifier})

def get_orientation(posten, request):
    orientation = 'HORIZONTAL'
    if posten.postenart.name == 'Zeitnote':
        orientation = 'VERTIKAL'
    if 'o' in request.GET:
        orientation = request.GET['o']
    return orientation

def create_postenblatt_table(startnummern, sets, orientation='HORIZONTAL'):
    header_row = []
    data_rows = []
    bewertungsarten = [s.bewertungsart.name for s in sets]
    if orientation == 'HORIZONTAL':
        # Startnummern horizontal, Bewertungsart vertikal
        header_row = startnummern
        for i, set in enumerate(sets):
            first_cell = bewertungsarten[i]
            next_cells = [form for form in set.forms]
            data_rows.append((first_cell, next_cells))
    else:
        # Startnummern vertikal, Bewertungsart horizontal
        header_row = bewertungsarten
        for i, startnummer in enumerate(startnummern):
            first_cell = startnummer
            next_cells = [set.forms[i] for set in sets]
            data_rows.append((first_cell, next_cells))
    return header_row, data_rows

def richtzeiten(request, jahr, wettkampf, disziplin):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    zeitposten = d.posten_set.filter(postenart__name='Zeitnote')
    if zeitposten.count() == 0:
        raise Http404("Es gibt gar keine Zeitposten")
    p = zeitposten[0]
    url = reverse(richtzeit, args=[jahr, wettkampf, disziplin, p.name])
    return HttpResponseRedirect(url)

def get_richtzeit_topn(disziplin):
    if disziplin.disziplinart.name == "Einzelfahren":
        return (read_topzeiten, "richtzeit_topn.html")
    else:
        return (read_sektionsfahren_topzeiten, "sektionsfahren_richtzeit_topn.html")

def richtzeiten_pdf(request, jahr, wettkampf, disziplin):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    flowables = _create_pdf_bestzeiten(d)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = smart_str('filename=richtzeiten-%s' % w.name)
    doc = create_rangliste_doctemplate(w)
    doc.build(flowables, filename=response)
    return response

def richtzeit(request, jahr, wettkampf, disziplin, posten, template='richtzeit.html'):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    p = Posten.objects.get(disziplin=d, name=posten)
    form = RichtzeitForm(p)
    zeitposten = d.posten_set.filter(postenart__name='Zeitnote')
    read_topzeiten, topn_template = get_richtzeit_topn(d)
    rangliste = list(read_topzeiten(p, topn=None))
    if 'orderByStnr' in request.GET:
        rangliste = sorted(rangliste, key=lambda k: k['startnummer_calc'])
    paginator = Paginator(rangliste, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, template, {'wettkampf': w, 'disziplin':
        d, 'posten': p, 'zeitposten': zeitposten, 'page_obj': page_obj,
        'form': form, 'topn_template': topn_template})

@permission_required('sasse.change_richtzeit')
def richtzeit_update(request, jahr, wettkampf, disziplin, posten):
    if request.method == 'POST':
        return richtzeit_post(request, jahr, wettkampf, disziplin, posten)
    return richtzeit(request, jahr, wettkampf, disziplin, posten, 'richtzeit_update.html')

@permission_required('sasse.change_richtzeit')
def richtzeit_post(request, jahr, wettkampf, disziplin, posten):
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    p = Posten.objects.get(disziplin=d, name=posten)
    form = RichtzeitForm(p, data=request.POST)
    if form.is_valid():
        form.save()
        url = reverse(richtzeit, args=[jahr, wettkampf, disziplin, posten])
        return HttpResponseRedirect(url)
    zeitposten = d.posten_set.filter(postenart__name='Zeitnote')
    read_topzeiten, topn_template = get_richtzeit_topn(d)
    rangliste = list(read_topzeiten(p, topn=None))
    return render(request, 'richtzeit_update.html', {'wettkampf': w,
        'disziplin': d, 'posten': p, 'zeitposten': zeitposten, 'rangliste':
        rangliste, 'form': form, 'topn_template': topn_template})

def notenliste(request, jahr, wettkampf, disziplin):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    posten = d.posten_set.all().select_related()
    notenliste = []
    searchform = SchiffeinzelFilterForm.create_with_sektion(d, request.GET)
    if searchform.is_valid():
        sektion = searchform.cleaned_data['sektion']
        startnummern = [schiff.startnummer for schiff in searchform.schiffe]
        notenliste = read_notenliste(d, posten, sektion, startnummern)
    paginator = Paginator(list(notenliste), 15, orphans=3)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, 'notenliste.html', {'wettkampf': w, 'disziplin':
        d, 'posten': posten, 'page_obj': page_obj, 'searchform': searchform}
        )

def notenliste_pdf(request, jahr, wettkampf, disziplin):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    posten = d.posten_set.all().select_related()
    searchform = SchiffeinzelFilterForm.create_with_sektion(d, request.GET)
    searchform.is_valid()
    sektion = searchform.cleaned_data['sektion']
    startnummern = [schiff.startnummer for schiff in searchform.schiffe]
    notenliste = read_notenliste(d, posten, sektion, startnummern)
    doc = create_notenliste_doctemplate(w, d)
    flowables = create_notenliste_flowables(posten, notenliste, sektion)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = smart_str('filename=notenliste')
    doc.build(flowables, filename=response)
    return response

def notenliste_pdf_all(request, jahr, wettkampf, disziplin):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    posten = d.posten_set.all().select_related()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = smart_str('filename=notenliste')
    doc = create_notenliste_doctemplate(w, d)
    flowables = []
    for sektion in Sektion.objects.all():
        schiffe = Schiffeinzel.objects.filter(disziplin=d, sektion=sektion)
        if schiffe:
            startnummern = [schiff.startnummer for schiff in schiffe]
            notenliste = read_notenliste(d, posten, sektion, startnummern)
            flowables += create_notenliste_flowables(posten, notenliste, sektion)
    doc.build(flowables, filename=response)
    return response

def rangliste(request, jahr, wettkampf, disziplin, kategorie=None):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    gestartete_kategorien = read_startende_kategorien(d)
    if kategorie:
        k = d.kategorien.get(name=kategorie)
    elif list(gestartete_kategorien):
        k = gestartete_kategorien[0]
    else:
        raise Http404("Die Startliste ist noch leer" % d)
    kranzlimite = read_kranzlimite(d, k)
    rangliste = read_rangliste(d, k)
    rangliste_sorted = sorted(rangliste, key=sort_rangliste)
    return render(request, 'rangliste.html', {'wettkampf': w, 'disziplin':
        d, 'kategorie': k, 'kategorien': gestartete_kategorien, 'rangliste':
        rangliste_sorted, 'kranzlimite': kranzlimite})

def rangliste_pdf(request, jahr, wettkampf, disziplin, kategorie):
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    k = d.kategorien.get(name=kategorie)
    flowables = _create_pdf_einzelfahren(d, k)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = smart_str('filename=rangliste-%s-kat-%s' % (w.name, k.name))
    doc = create_rangliste_doctemplate(w)
    doc.build(flowables, filename=response)
    return response

def rangliste_pdf_all(request, jahr, wettkampf, disziplin):
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    flowables = []
    for k in read_startende_kategorien(d):
        flowables.extend(_create_pdf_einzelfahren(d, k))
    flowables.extend(_create_pdf_bestzeiten(d))
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = smart_str('filename=rangliste-%s' % w.name)
    doc = create_rangliste_doctemplate(w)
    doc.build(flowables, filename=response)
    return response

def rangliste_xlsx_all(request, jahr, wettkampf, disziplin):
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    rangliste = read_rangliste(d, None)
    def sort_rangliste_excel(row):
        rang = row['rang']
        if isinstance(rang, int):
            return rang
        else:
            return 10000 # Doppelstarter, Ausgeschieden, ...
    rangliste_sorted = sorted(rangliste, key=sort_rangliste_excel)
    wb = Workbook()
    sheet = wb.active
    for i, row in enumerate(rangliste_sorted):
        if i == 0:
            headers = list(row.keys())
            sheet.append(headers)
        row['kranz'] = True if row['kranz'] == 1 else False
        row['zeit_tot'] = row['zeit_tot'].zeit
        row['punkt_tot'] = row['punkt_tot'].note
        row['vorderfahrer_jg'] = row['vorderfahrer_jg'].year
        row['steuermann_jg'] = row['steuermann_jg'].year
        sheet.append(list(row.values()))
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = smart_str('attachment; filename=rangliste-%s-%s-%s.xlsx' % (jahr, wettkampf, disziplin))
    wb.save(response)
    return response

def beste_schiffe(request, jahr, wettkampf, disziplin):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    typ = request.GET.get('typ', 'Amerikaner')
    if typ == 'Amerikaner':
        rangliste = read_beste_fahrerpaare(d, ['C','D'], 6)
    elif typ == 'Lichtensteiner':
        rangliste = read_beste_fahrerpaare(d, ['II','III'], 2)
    else:
        raise Http404("Query für Typ %s existiert nicht" % typ)
    return render(request, 'beste_schiffe.html', {
        'wettkampf': w, 'disziplin': d, 'typ': typ, 'rangliste': rangliste})

def beste_saisonpaare(request, jahr, wettkampf, disziplin, kategorie=None):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    wettkaempfe = _select_wettkaempfe_beste_saisonpaare(jahr)
    kategorien = Kategorie.objects.filter(name__in=["I","II","III","FII","FIII","F","D","C"])
    if kategorie:
        k = Kategorie.objects.get(name=kategorie)
    else:
        k = kategorien[0]
    rangliste = read_beste_saisonpaare(wettkaempfe, k.name)
    return render(request, 'beste_saisonpaare.html', {
        'wettkampf': w, 'disziplin': d, 'jahr': jahr, 'kategorien': kategorien,
        'wettkaempfe': wettkaempfe, 'kategorie': k, 'rangliste': rangliste})

def beste_saisonpaare_pdf(request, jahr, wettkampf, disziplin):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    wettkaempfe = _select_wettkaempfe_beste_saisonpaare(jahr)
    kategorien = Kategorie.objects.filter(name__in=["I","II","III","FII","FIII","F","D","C"])
    all_rangliste = []
    for k in kategorien:
        rangliste = read_beste_saisonpaare(wettkaempfe, k.name)
        rangliste = list(rangliste)[:3]
        all_rangliste.append((k.name, rangliste))
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = smart_str('filename=beste-saisonpaare-%s' % (jahr,))
    flowables = create_beste_saisonpaare_flowables(wettkaempfe, all_rangliste)
    doc = create_beste_saisonpaare_doctemplate(jahr, wettkaempfe)
    doc.build(flowables, filename=response)
    return response

def _select_wettkaempfe_beste_saisonpaare(jahr):
    wettkaempfe = []
    for item in Disziplin.objects.select_related().filter(
            disziplinart__name="Einzelfahren",
            wettkampf__von__year=jahr).order_by('wettkampf__von'):
        if item.wettkampf.name in ('7er-Club-Mix', '7er-Club-Endfahren', 'OldieCup'):
            continue
        if item.wettkampf not in wettkaempfe:
            wettkaempfe.append(item.wettkampf)
    return wettkaempfe

def aelteste_fahrerpaare(request, jahr, wettkampf, disziplin):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    rangliste = read_aelteste_fahrerpaare(d)
    paginator = Paginator(rangliste, 25, orphans=3)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, 'aelteste_fahrerpaare.html', {
        'wettkampf': w, 'disziplin': d, 'page_obj': page_obj})

def notenblatt(request, jahr, wettkampf, disziplin, startnummer=None):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    if startnummer:
        s = Schiffeinzel.objects.select_related().get(disziplin=d,
                startnummer=startnummer)
    else:
        s = Schiffeinzel.objects.select_related().filter(disziplin=d)[0]
    try:
        next = Schiffeinzel.objects.filter(disziplin=d,
                startnummer__gt=s.startnummer)[0].startnummer
    except IndexError:
        next = None
    posten_werte = read_notenblatt(d, s)
    return render(request, 'notenblatt.html', {'wettkampf': w, 'disziplin':
        d, 'schiff': s, 'posten_werte': posten_werte, 'next': next})

def notenblatt_pdf(request, jahr, wettkampf, disziplin, startnummer):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    s = Schiffeinzel.objects.select_related().get(disziplin=d,
            startnummer=startnummer)
    posten_werte = read_notenblatt(d, s)
    doc = create_notenblatt_doctemplate(w, d)
    flowables = create_notenblatt_flowables(posten_werte, s)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = smart_str('filename=notenblatt-%s' % startnummer)
    doc.build(flowables, filename=response)
    return response

def notenblaetter_pdf(request, jahr, wettkampf, disziplin):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    searchform = SchiffeinzelFilterForm.create_with_sektion(d, request.GET)
    searchform.is_valid()
    schiffe = searchform.schiffe
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = smart_str('filename=notenblaetter')
    doc = create_notenblatt_doctemplate(w, d)
    flowables = []
    for s in schiffe:
        posten_werte = read_notenblatt(d, s)
        flowables += create_notenblatt_flowables(posten_werte, s)
    doc.build(flowables, filename=response)
    return response

def kranzlimiten(request, jahr, wettkampf, disziplin):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    kranzlimiten = read_kranzlimiten(d)
    return render(request, 'kranzlimiten.html', {'wettkampf': w,
        'disziplin': d, 'kranzlimiten': kranzlimiten})

@permission_required("sasse.change_kranzlimite")
def kranzlimiten_update(request, jahr, wettkampf, disziplin):
    if request.method == 'POST':
        if 'set_defaults' in request.POST:
            return kranzlimiten_set_defaults(request, jahr, wettkampf, disziplin)
        else:
            return kranzlimiten_put(request, jahr, wettkampf, disziplin)
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    limite_pro_kategorie = read_kranzlimite_pro_kategorie(d)
    initial = []
    for k in read_startende_kategorien(d):
        kl = limite_pro_kategorie.get(k.id, Kranzlimite(disziplin=d, kategorie=k))
        dict = {'kl_id': kl.id, 'kl_wert': kl.wert, 'kat_id': k.id, 'kat_name': k.name,}
        initial.append(dict)
    KranzlimiteFormSet = formset_factory(KranzlimiteForm, extra=0)
    formset = KranzlimiteFormSet(initial=initial)
    return render(request, 'kranzlimiten_update.html',
            {'wettkampf': w, 'disziplin': d, 'formset': formset})

@permission_required("sasse.change_kranzlimite")
def kranzlimiten_put(request, jahr, wettkampf, disziplin):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    KranzlimiteFormSet = formset_factory(KranzlimiteForm, extra=0)
    formset = KranzlimiteFormSet(request.POST)
    if formset.is_valid():
        for form in formset.forms:
            data = form.cleaned_data
            kl = Kranzlimite(id=data['kl_id'], wert=data['kl_wert'],
                    kategorie_id=data['kat_id'], disziplin=d)
            if kl.wert:
                kl.save()
            elif kl.id and not kl.wert:
                kl.delete()
        url = reverse(kranzlimiten, args=[jahr, wettkampf, d.name])
        return HttpResponseRedirect(url)
    return render(request, 'kranzlimiten_update.html',
            {'wettkampf': w, 'disziplin': d, 'formset': formset})

@permission_required("sasse.change_kranzlimite")
def kranzlimiten_set_defaults(request, jahr, wettkampf, disziplin):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    limite_pro_kategorie = read_kranzlimite_pro_kategorie(d)
    for k in read_startende_kategorien(d):
        kl = limite_pro_kategorie.get(k.id, Kranzlimite(disziplin=d, kategorie=k))
        top25 = read_anzahl_wettkaempfer(d, k) * 0.25
        kraenze = 0
        for row in read_rangliste(d, k):
            kraenze += 2
            if row['steuermann_ist_ds']:
                kraenze -= 1
            if row['vorderfahrer_ist_ds']:
                kraenze -= 1
            if kraenze > top25:
                limite = row['punkt_tot'].note
                kl.wert = limite
                kl.save()
                break
    url = reverse(kranzlimiten, args=[jahr, wettkampf, d.name])
    return HttpResponseRedirect(url)

def doppelstarter_einzelfahren(request, jahr, wettkampf):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    einzelfahren = Disziplinart.objects.get(name="Einzelfahren")
    doppelstarter = read_doppelstarter(w, einzelfahren)
    return render(request, 'doppelstarter_einzelfahren.html', {'wettkampf': w,
        'doppelstarter': doppelstarter})

def startlisten_einzelfahren_export(request, jahr, wettkampf):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    response = HttpResponse(content_type='text/csv')
    now = datetime.datetime.now()
    filename = "startlisten-einzelfahren-%s.csv" % now.strftime("%Y%m%d%H%M")
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    eai_startliste.dump(w, response)
    return response

@permission_required("sasse.change_schiffeinzel")
@transaction.atomic
def startlisten_einzelfahren_import(request, jahr, wettkampf):
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    if request.method == 'POST':
        form = StartlisteUploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            eai_startliste.load(w, request.FILES['startliste'])
            url = reverse(wettkampf_get, args=[w.jahr(), w.name])
            return HttpResponseRedirect(url)
    else:
        form = StartlisteUploadFileForm()
    return render(request, 'startlisten_einzelfahren_upload.html',
            {'wettkampf': w, 'form': form})

@permission_required("sasse.change_schiffeinzel")
@transaction.atomic
def zeiten_einzelfahren_import(request, jahr, wettkampf, disziplin, posten):
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    p = Posten.objects.get(disziplin=d, name=posten)
    success = 0
    failed = []
    if request.method == 'POST':
        form = EinzelfahrenZeitUploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            success, failed = eai_zeiten.load_einzelfahren(w, d, p, request.FILES['zeiten'])
    else:
        form = EinzelfahrenZeitUploadFileForm()
    total = success + len(failed)
    return render(request, 'zeiten_einzelfahren_upload.html',
            {'wettkampf': w, 'disziplin': d, 'posten': p, 'form': form,
                'success': success, 'failed': failed, 'total': total})

def einzelfahren_null_zeiten(request, jahr, wettkampf, disziplin):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    null_zeiten = list(read_einzelfahren_null_zeiten(d))
    return render(request, 'einzelfahren_null_zeiten.html',
            {'wettkampf': d.wettkampf, 'disziplin': d, 'null_zeiten':
                null_zeiten})

@permission_required("sasse.change_schiffeinzel")
@transaction.atomic
def noten_einzelfahren_import(request, jahr, wettkampf, disziplin, posten):
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    p = Posten.objects.get(disziplin=d, name=posten)
    success = 0
    failed = []
    if request.method == 'POST':
        form = EinzelfahrenNotenUploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            success, failed = eai_noten.load_pfeiler(w, d, p,
                    request.FILES['noten'])
    else:
        form = EinzelfahrenNotenUploadFileForm()
    total = success + len(failed)
    return render(request, 'noten_einzelfahren_upload.html',
            {'wettkampf': w, 'disziplin': d, 'posten': p, 'form': form,
                'success': success, 'failed': failed, 'total': total})

#
# Sektionsfahren
#
def sektionsfahren_get(request, jahr, wettkampf):
    d = Disziplin.objects.select_related().get(
            disziplinart__name="Sektionsfahren",
            wettkampf__name=wettkampf,
            wettkampf__von__year=jahr)
    return render(request, "einzelfahren.html",
            {'wettkampf': d.wettkampf, 'disziplin': d})

def sektionsfahren_startliste(request, jahr, wettkampf):
    assert request.method == 'GET'
    d = Disziplin.objects.select_related().get(
            disziplinart__name="Sektionsfahren",
            wettkampf__name=wettkampf,
            wettkampf__von__year=jahr)
    w = d.wettkampf
    startliste = Sektionsfahrengruppe.objects.with_counts(d)
    sort = request.GET.get('o')
    if sort and sort == 'Startnr':
        startliste = sorted(startliste, key=lambda k: k.startnummer)
    elif sort and sort == 'Gruppe':
        startliste = sorted(startliste, key=lambda k: k.name)
    return render(request, 'sektionsfahren_startliste.html', {
        'wettkampf': w, 'disziplin': d, 'startliste': startliste})

@permission_required('sasse.add_gruppe')
def sektionsfahren_gruppe_add(request, jahr, wettkampf):
    if request.method == 'POST':
        return sektionsfahren_gruppe_post(request, jahr, wettkampf)
    assert request.method == 'GET'
    d = Disziplin.objects.select_related().get(
            disziplinart__name="Sektionsfahren",
            wettkampf__name=wettkampf,
            wettkampf__von__year=jahr)
    w = d.wettkampf
    form = GruppeForm(d, initial={'sektion': request.GET.get('sektion')})
    return render(request, 'sektionsfahren_gruppe_add.html', {
        'wettkampf': d.wettkampf, 'disziplin': d, 'form': form})

@permission_required('sasse.add_gruppe')
def sektionsfahren_gruppe_post(request, jahr, wettkampf):
    assert request.method == 'POST'
    d = Disziplin.objects.select_related().get(
            disziplinart__name="Sektionsfahren",
            wettkampf__name=wettkampf,
            wettkampf__von__year=jahr)
    form = GruppeForm(d, request.POST.copy())
    if form.is_valid():
        gruppe = form.save()
        url = reverse(sektionsfahren_gruppe_get, args=[jahr, wettkampf, gruppe.name])
        return HttpResponseRedirect(url)
    return render(request, 'sektionsfahren_gruppe_add.html',
            {'wettkampf': d.wettkampf, 'disziplin': d, 'form': form})

@permission_required('sasse.delete_gruppe')
def sektionsfahren_gruppe_delete(request, jahr, wettkampf, gruppe):
    g = Sektionsfahrengruppe.objects.select_related().get(
            name=gruppe,
            disziplin__disziplinart__name="Sektionsfahren",
            disziplin__wettkampf__name=wettkampf,
            disziplin__wettkampf__von__year=jahr)
    if request.method == 'POST':
        g.delete()
        url = reverse(sektionsfahren_startliste, args=[jahr, wettkampf])
        return HttpResponseRedirect(url)
    d = g.disziplin
    w = d.wettkampf
    return render(request, 'sektionsfahren_gruppe_delete.html', {
        'wettkampf': w, 'disziplin': d, 'gruppe': g})

def sektionsfahren_gruppe_get(request, jahr, wettkampf, gruppe):
    assert request.method == 'GET'
    g = Sektionsfahrengruppe.objects.select_related().get(
            name=gruppe,
            disziplin__disziplinart__name="Sektionsfahren",
            disziplin__wettkampf__name=wettkampf,
            disziplin__wettkampf__von__year=jahr)
    d = g.disziplin
    w = d.wettkampf
    form = SchiffsektionForm(g)
    return render(request, 'sektionsfahren_gruppe.html', {
        'wettkampf': w, 'disziplin': d, 'gruppe': g, 'form': form})

@permission_required('sasse.change_gruppe')
def sektionsfahren_gruppe_update(request, jahr, wettkampf, gruppe):
    g = Sektionsfahrengruppe.objects.select_related().get(
            name=gruppe,
            disziplin__disziplinart__name="Sektionsfahren",
            disziplin__wettkampf__name=wettkampf,
            disziplin__wettkampf__von__year=jahr)
    d = g.disziplin
    w = d.wettkampf
    if request.method == 'POST':
        form = GruppeForm(d, request.POST.copy(), instance=g)
        if form.is_valid():
            g = form.save()
            url = reverse(sektionsfahren_gruppe_get, args=[jahr, wettkampf, g.name])
            return HttpResponseRedirect(url)
    else:
        form = GruppeForm(d, instance=g)
    return render(request, 'sektionsfahren_gruppe_update.html', {
        'wettkampf': w, 'disziplin': d, 'gruppe': g, 'form': form})

@permission_required('sasse.add_schiffsektion')
def sektionsfahren_schiff_post(request, jahr, wettkampf, gruppe):
    assert request.method == 'POST'
    g = Sektionsfahrengruppe.objects.select_related().get(
            name=gruppe,
            disziplin__disziplinart__name="Sektionsfahren",
            disziplin__wettkampf__name=wettkampf,
            disziplin__wettkampf__von__year=jahr)
    form = SchiffsektionForm(g, request.POST.copy())
    if form.is_valid():
        schiff = form.save()
        url = reverse(sektionsfahren_gruppe_get, args=[jahr, wettkampf, gruppe])
        return HttpResponseRedirect(url)
    d = g.disziplin
    w = d.wettkampf
    return render(request, 'sektionsfahren_gruppe.html', {
        'wettkampf': w, 'disziplin': d, 'gruppe': g, 'form': form})

@permission_required('sasse.change_schiffsektion')
def sektionsfahren_schiff_update(request, jahr, wettkampf, gruppe, position):
    schiff = Schiffsektion.objects.select_related().get(
            position=position,
            gruppe__name=gruppe,
            disziplin__disziplinart__name="Sektionsfahren",
            disziplin__wettkampf__name=wettkampf,
            disziplin__wettkampf__von__year=jahr)
    g = schiff.gruppe
    d = g.disziplin
    w = d.wettkampf
    if request.method == 'POST':
        form = SchiffsektionForm(g, request.POST.copy(), instance=schiff)
        if form.is_valid():
            if 'delete' in request.POST:
                schiff.delete()
            else:
                form.save()
            url = reverse(sektionsfahren_gruppe_get, args=[jahr, wettkampf, gruppe])
            return HttpResponseRedirect(url)
    else:
        form = SchiffsektionForm(g, instance=schiff)
    return render(request, 'sektionsfahren_schiff_update.html', {
        'wettkampf': w, 'disziplin': d, 'schiff': schiff, 'form': form})

@permission_required('sasse.change_gruppe')
def sektionsfahren_gruppe_abzug(request, jahr, wettkampf, gruppe):
    g = Sektionsfahrengruppe.objects.select_related().get(
            name=gruppe,
            disziplin__disziplinart__name="Sektionsfahren",
            disziplin__wettkampf__name=wettkampf,
            disziplin__wettkampf__von__year=jahr)
    d = g.disziplin
    w = d.wettkampf
    if request.method == 'POST':
        form = SektionsfahrenGruppeAbzugForm(request.POST, instance=g)
        if form.is_valid():
            g = form.save()
            url = form.cleaned_data['referrer']
            return HttpResponseRedirect(url)
    else:
        referrer = request.META['HTTP_REFERER']
        form = SektionsfahrenGruppeAbzugForm(initial={'referrer': referrer}, instance=g)
    return render(request, 'sektionsfahren_gruppe_abzug_update.html', {
        'wettkampf': w, 'disziplin': d, 'gruppe': g, 'form': form})

def sektionsfahren_postenblatt(request, jahr, wettkampf, posten=None):
    if posten:
        p = Posten.objects.select_related().get(
                name=posten,
                disziplin__disziplinart__name="Sektionsfahren",
                disziplin__wettkampf__name=wettkampf,
                disziplin__wettkampf__von__year=jahr)
        d = p.disziplin
    else:
        d = Disziplin.objects.select_related().get(
                disziplinart__name="Sektionsfahren",
                wettkampf__name=wettkampf,
                wettkampf__von__year=jahr)
        p = d.posten_set.all()[0]
    return postenblatt(request, jahr, wettkampf, d.name, p.name)

def sektionsfahren_rangliste(request, jahr, wettkampf):
    assert request.method == 'GET'
    d = Disziplin.objects.select_related().get(
            disziplinart__name="Sektionsfahren",
            wettkampf__name=wettkampf,
            wettkampf__von__year=jahr)
    w = d.wettkampf
    rangliste = read_sektionsfahren_rangliste(d)
    return render(request, 'sektionsfahren_rangliste.html', {
        'wettkampf': w, 'disziplin': d, 'rangliste': rangliste})

def sektionsfahren_rangliste_pdf(request, jahr, wettkampf):
    assert request.method == 'GET'
    d = Disziplin.objects.select_related().get(
            disziplinart__name="Sektionsfahren",
            wettkampf__name=wettkampf,
            wettkampf__von__year=jahr)
    w = d.wettkampf
    flowables = _create_pdf_sektionsfahren(d)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = smart_str('filename=rangliste-%s-%s' % (w.name, d.name))
    doc = create_rangliste_doctemplate(w)
    doc.build(flowables, filename=response)
    return response

def sektionsfahren_kranzlimiten(request, jahr, wettkampf):
    assert request.method == 'GET'
    d = Disziplin.objects.select_related().get(
            disziplinart__name="Sektionsfahren",
            wettkampf__name=wettkampf,
            wettkampf__von__year=jahr)
    w = d.wettkampf
    limiten, created = SektionsfahrenKranzlimiten.objects.get_or_create(disziplin=d)
    return render(request, 'sektionsfahren_kranzlimiten.html', {
        'wettkampf': w, 'disziplin': d, 'limiten': limiten})

@permission_required('sasse.change_sektionsfahrenkranzlimiten')
def sektionsfahren_kranzlimiten_update(request, jahr, wettkampf):
    d = Disziplin.objects.select_related().get(
            disziplinart__name="Sektionsfahren",
            wettkampf__name=wettkampf,
            wettkampf__von__year=jahr)
    w = d.wettkampf
    limiten, created = SektionsfahrenKranzlimiten.objects.get_or_create(disziplin=d)
    if request.method == 'POST':
        form = SektionsfahrenKranzlimitenForm(request.POST, instance=limiten)
        if form.is_valid():
            g = form.save()
            url = reverse(sektionsfahren_rangliste, args=[jahr, wettkampf])
            return HttpResponseRedirect(url)
    else:
        form = SektionsfahrenKranzlimitenForm(instance=limiten)
    return render(request, 'sektionsfahren_kranzlimiten_update.html', {
        'wettkampf': w, 'disziplin': d, 'form': form})

def sektionsfahren_rangliste_gruppe(request, jahr, wettkampf):
    assert request.method == 'GET'
    d = Disziplin.objects.select_related().get(
            disziplinart__name="Sektionsfahren",
            wettkampf__name=wettkampf,
            wettkampf__von__year=jahr)
    w = d.wettkampf
    rangliste = read_sektionsfahren_rangliste_gruppe(d)
    return render(request, 'sektionsfahren_rangliste_gruppe.html', {
        'wettkampf': w, 'disziplin': d, 'rangliste': rangliste})

def sektionsfahren_rangliste_schiff(request, jahr, wettkampf):
    assert request.method == 'GET'
    d = Disziplin.objects.select_related().get(
            disziplinart__name="Sektionsfahren",
            wettkampf__name=wettkampf,
            wettkampf__von__year=jahr)
    w = d.wettkampf
    rangliste = list(read_sektionsfahren_rangliste_schiff(d))
    paginator = Paginator(rangliste, 10, orphans=3)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, 'sektionsfahren_rangliste_schiff.html', {
        'wettkampf': w, 'disziplin': d, 'page_obj': page_obj})

def sektionsfahren_rangliste_fahrchef(request, jahr, wettkampf):
    assert request.method == 'GET'
    d = Disziplin.objects.select_related().get(
            disziplinart__name="Sektionsfahren",
            wettkampf__name=wettkampf,
            wettkampf__von__year=jahr)
    w = d.wettkampf
    vorherige_disziplin = Disziplin.objects.exclude(id=d.id).filter(
            disziplinart__name="Sektionsfahren",
            wettkampf__EIDG=True,
            wettkampf__von__year__lt=jahr).order_by("-wettkampf__von").first()
    if vorherige_disziplin is None:
        raise Http404("Das vorherige Eidgenössische nicht vorhanden")
    vorherige_rangliste = read_sektionsfahren_rangliste(vorherige_disziplin)
    vorherige_totals = {}
    for r in vorherige_rangliste:
        fahrchef = r['gruppen'][0].chef
        total = r['total']
        vorherige_totals[fahrchef] = total
    aktuelle_rangliste = read_sektionsfahren_rangliste(d)
    rangliste = []
    for r in aktuelle_rangliste:
        fahrchef = r['gruppen'][0].chef
        aktuelles_total = r['total'] * 2
        vorheriges_total = vorherige_totals.get(fahrchef)
        if vorheriges_total:
            rangliste.append({
                'fahrchef': fahrchef,
                'vorheriges_total': vorheriges_total,
                'aktuelles_total': aktuelles_total,
                'total': vorheriges_total + aktuelles_total,
                })
    rangliste = sorted(rangliste, key=lambda k: k['total'], reverse=True)
    rang = 0
    for r in rangliste:
        rang += 1
        r['rang'] = rang
    return render(request, 'sektionsfahren_rangliste_fahrchef.html', {
        'wettkampf': w, 'disziplin': d, 'rangliste': rangliste,
        'vorheriger_wettkampf': vorherige_disziplin.wettkampf})

def sektionsfahren_notenblatt(request, jahr, wettkampf, sektion_name):
    assert request.method == 'GET'
    d = Disziplin.objects.select_related().get(
            disziplinart__name="Sektionsfahren",
            wettkampf__name=wettkampf,
            wettkampf__von__year=jahr)
    w = d.wettkampf
    result = {}
    rangliste = read_sektionsfahren_rangliste(d)
    for item in rangliste:
        if item['name'] == sektion_name:
            result = item
            break
    return render(request, 'sektionsfahren_notenblatt.html', {
        'wettkampf': w, 'disziplin': d, 'sektion': result})

def sektionsfahren_notenblatt_pdf(request, jahr, wettkampf, sektion_name):
    assert request.method == 'GET'
    d = Disziplin.objects.select_related().get(
            disziplinart__name="Sektionsfahren",
            wettkampf__name=wettkampf,
            wettkampf__von__year=jahr)
    w = d.wettkampf
    sektion = {}
    rangliste = read_sektionsfahren_rangliste(d)
    for item in rangliste:
        if item['name'] == sektion_name:
            sektion = item
            break
    doc = create_sektionsfahren_notenblatt_doctemplate(w, d)
    flowables = create_sektionsfahren_notenblatt_flowables(sektion)
    for gruppe in sektion['gruppen']:
        notenliste = read_sektionsfahren_notenblatt_gruppe(gruppe)
        notenliste = regroup_notenliste(notenliste, gruppe.anz_schiffe())
        flowables += create_sektionsfahren_notenblatt_gruppe_flowables(gruppe, notenliste)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = smart_str('filename=notenblatt-%s' % sektion_name)
    doc.build(flowables, filename=response)
    return response

def sektionsfahren_notenblatt_pdf_all(request, jahr, wettkampf):
    assert request.method == 'GET'
    d = Disziplin.objects.select_related().get(
            disziplinart__name="Sektionsfahren",
            wettkampf__name=wettkampf,
            wettkampf__von__year=jahr)
    w = d.wettkampf
    doc = create_sektionsfahren_notenblatt_doctemplate(w, d)
    rangliste = read_sektionsfahren_rangliste(d)
    rangliste = sorted(rangliste, key=lambda k: k['name'])
    flowables = []
    for sektion in rangliste:
        flowables.extend(create_sektionsfahren_notenblatt_flowables(sektion))
        for gruppe in sektion['gruppen']:
            notenliste = read_sektionsfahren_notenblatt_gruppe(gruppe)
            notenliste = regroup_notenliste(notenliste, gruppe.anz_schiffe())
            flowables.extend(create_sektionsfahren_notenblatt_gruppe_flowables(gruppe, notenliste))
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = smart_str('filename=notenblaetter-sektionsfahren')
    doc.build(flowables, filename=response)
    return response

def sektionsfahren_notenblatt_gruppe(request, jahr, wettkampf, gruppe):
    assert request.method == 'GET'
    d = Disziplin.objects.select_related().get(
            disziplinart__name="Sektionsfahren",
            wettkampf__name=wettkampf,
            wettkampf__von__year=jahr)
    w = d.wettkampf
    # Muss Rangliste lesen wegen den berechneten Werte der Gruppe
    rangliste = read_sektionsfahren_rangliste_gruppe(d)
    for item in rangliste:
        if item.name == gruppe:
            g = item
            break
    notenliste = read_sektionsfahren_notenblatt_gruppe(g)
    notenliste = regroup_notenliste(notenliste, g.anz_schiffe())
    return render(request, 'sektionsfahren_notenblatt_gruppe.html', {
        'wettkampf': w, 'disziplin': d, 'gruppe': g, 'notenliste': notenliste,
        'schiff_range': list(range(1, g.anz_schiffe() + 1))})

def regroup_notenliste(notenliste, anzahl_schiffe):
    """
    input = [{
        'gruppe': 'Schmerikon',
        'postenart': 'Anmeldung (Sektionsfahren)',
        'posten': 'A',
        'schiff_1': 10.0, 'schiff_2': 10.0, 'schiff_3': 10.0, 'schiff_4': 7.8,
        }, {
        'gruppe': 'Schmerikon',
        'postenart': 'Gemeinsame Stachelfahrt',
        'posten': 'B-C1',
        'schiff_1': 10.0, 'schiff_2': 9.0, 'schiff_3': 8.0, 'schiff_4': 10.0,
        }, {
        'gruppe': 'Schmerikon',
        'postenart': 'Gemeinsame Stachelfahrt',
        'posten': 'B-C2',
        'schiff_1': 7.0, 'schiff_2': 9.0, 'schiff_3': 10.0, 'schiff_4': 10.0,
        }, ]

    output = [{
        'gruppe': 'Schmerikon',
        'postenart': 'Anmeldung (Sektionsfahren)',
        'posten': 'A',
        'colspan': '2',
        'noten': (10.0, 10.0, 10.0, 10.0)
        }, {
        'gruppe': 'Schmerikon',
        'postenart': 'Gemeinsame Stachelfahrt',
        'posten': 'B-C',
        'colspan': '1',
        'noten': (9.0, 8.0, 10.0, 10.0, 10.0, 9.0, 10.0, 7.0, 10.0, 10.0),
        }, ]
    """

    from itertools import groupby
    def extract_posten(row):
        posten = row.get('posten')
        postenart = row.get('postenart')
        if posten and posten[-1] in ('1','2'):
            posten = posten[:-1]
        return posten, postenart
    for (posten, postenart), group in groupby(notenliste, extract_posten):
        noten = []
        for row in group:
            for i in range(1, anzahl_schiffe + 1):
                note = row['schiff_%d' % i]
                noten.append(str(note).replace(".0",""))
        anz_durchgaenge = len(noten) / anzahl_schiffe
        if anz_durchgaenge == 2:
            x = []
            for i, note in enumerate(noten[:anzahl_schiffe]):
                x.append(note)
                x.append(noten[i+anzahl_schiffe])
            noten = x
        colspan = 3 - anz_durchgaenge
        yield {'posten': posten, 'postenart': postenart, 'colspan': colspan, 'noten': noten}

def sektionsfahren_notenblatt_gruppe_pdf(request, jahr, wettkampf, gruppe):
    assert request.method == 'GET'
    d = Disziplin.objects.select_related().get(
            disziplinart__name="Sektionsfahren",
            wettkampf__name=wettkampf,
            wettkampf__von__year=jahr)
    w = d.wettkampf
    # Muss Rangliste lesen wegen den berechneten Werte der Gruppe
    rangliste = read_sektionsfahren_rangliste_gruppe(d)
    for item in rangliste:
        if item.name == gruppe:
            g = item
            break
    notenliste = read_sektionsfahren_notenblatt_gruppe(g)
    notenliste = regroup_notenliste(notenliste, g.anz_schiffe())
    doc = create_sektionsfahren_notenblatt_gruppe_doctemplate(w, d)
    flowables = create_sektionsfahren_notenblatt_gruppe_flowables(g, notenliste)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = smart_str('filename=notenblatt-%s' % g.name)
    doc.build(flowables, filename=response)
    return response

@permission_required('sasse.change_gruppe')
@transaction.atomic
def zeiten_sektionsfahren_import(request, jahr, wettkampf, disziplin, posten):
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    p1 = Posten.objects.get(disziplin=d, name=posten[:-1] + "1")
    p2 = Posten.objects.get(disziplin=d, name=posten[:-1] + "2")
    success = 0
    failed = []
    SektionsfahrenZeitUploadFormSet = formset_factory(SektionsfahrenZeitUploadForm, extra=0)
    if request.method == 'POST':
        form = EinzelfahrenZeitUploadFileForm(request.POST, request.FILES)
        formset = SektionsfahrenZeitUploadFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            csvfile = request.FILES['zeiten']
            success, failed = eai_zeiten.load_sektionsfahren(p1, p2, formset, csvfile)
    else:
        form = EinzelfahrenZeitUploadFileForm()
        initial = []
        for g in Sektionsfahrengruppe.objects.with_counts(d):
            initial.append({'gruppe_id': g.id, 'gruppe_name': g.name})
        formset = SektionsfahrenZeitUploadFormSet(initial=initial)
    total = success + len(failed)
    return render(request, 'zeiten_sektionsfahren_upload.html',
            {'wettkampf': w, 'disziplin': d, 'posten1': p1, 'posten2': p2,
                'form': form, 'formset': formset, 'success': success, 'failed':
                failed, 'total': total})

def sektionsfahren_null_zeiten(request, jahr, wettkampf, disziplin):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    null_zeiten = list(read_sektionsfahren_null_zeiten(d))
    return render(request, 'sektionsfahren_null_zeiten.html',
            {'wettkampf': d.wettkampf, 'disziplin': d, 'null_zeiten':
                null_zeiten})

#
# Spezialwettkaempfe
#

def _get_spezialwettkampf(jahr, wettkampf, disziplinart):
    return Disziplin.objects.select_related().get(
            disziplinart__name=disziplinart,
            wettkampf__name=wettkampf,
            wettkampf__von__year=jahr)

def _get_spezialwettkampf_kat(gestartete_kategorien, kategorie):
    if kategorie:
        aktuelle_kategorie = kategorie
    elif len(gestartete_kategorien) > 0:
        aktuelle_kategorie = gestartete_kategorien[0]
    else:
        raise Http404("Es sind noch keine Daten vorhanden")
    return aktuelle_kategorie

def _get_spezialwettkampf_limite(disziplin, aktuelle_kategorie):
    kranzlimite = None
    q = SpezialwettkaempfeKranzlimite.objects.filter(
            disziplin=disziplin, kategorie=aktuelle_kategorie)
    if q.count() > 0:
        kranzlimite = q[0].zeit
    return kranzlimite

def _create_spezialwettkampf_rangliste(rangliste, kranzlimite):
    result = []
    rang = 1
    anz_mit_kranz = 0
    previous_row = None
    trailer_indexes = []
    for i, row in enumerate(rangliste):
        row.kranz = False
        if row.disqualifiziert or row.ausgeschieden:
            trailer_indexes.append(i)
            if row.disqualifiziert:
                row.rang = "DISQ"
            if row.ausgeschieden:
                row.rang = "AUSG"
        else:
            if previous_row is not None and row.zeit == previous_row.zeit:
                row.rang = previous_row.rang
            else:
                row.rang = rang
            rang += 1
            if kranzlimite is not None and row.zeit <= kranzlimite:
                row.kranz = True
                anz_mit_kranz += 1
        previous_row = row
        result.append(row)
    # Move ausgeschieden/disqualifizert to the end
    if trailer_indexes:
        trailer_rows = []
        for i in trailer_indexes:
            trailer_rows.append(result.pop(i))
        result.extend(trailer_rows)
    kranz_prozent = round(((anz_mit_kranz * 1.0) / len(rangliste)) * 100, 1)
    return result, kranz_prozent

def _do_spezialwettkampf_get(request, jahr, wettkampf, disziplinart):
    d = _get_spezialwettkampf(jahr, wettkampf, disziplinart)
    return render(request, "spezialwettkaempfe.html",
            {'wettkampf': d.wettkampf, 'disziplin': d})

def _do_kranzlimite_update(request, jahr, wettkampf, disziplin, kategorie, redirect_view):
    limite, created = SpezialwettkaempfeKranzlimite.objects.get_or_create(
            disziplin=disziplin, kategorie=kategorie, defaults={'zeit': 0})
    if request.method == 'POST':
        form = SpezialwettkaempfeKranzlimiteForm(request.POST, instance=limite)
        if form.is_valid():
            obj = form.save()
            url = reverse(redirect_view, args=[jahr, wettkampf, kategorie])
            return HttpResponseRedirect(url)
    else:
        form = SpezialwettkaempfeKranzlimiteForm(instance=limite)
    return render(request, 'spezialwettkaempfe_kranzlimite_update.html', {
        'wettkampf': disziplin.wettkampf, 'disziplin': disziplin, 'form': form})

#
# Schwimmen
#

def schwimmen_get(request, jahr, wettkampf):
    return _do_spezialwettkampf_get(request, jahr, wettkampf, "Schwimmen")

@permission_required('sasse.change_gruppe')
def schwimmen_eingabe(request, jahr, wettkampf):
    d = _get_spezialwettkampf(jahr, wettkampf, "Schwimmen")
    if request.method == 'POST':
        form = SchwimmerForm(d, request.POST.copy())
        if form.is_valid():
            form.save()
            url = reverse(schwimmen_eingabe, args=[jahr, wettkampf])
            return HttpResponseRedirect(url)
    else:
        form = SchwimmerForm(d)
    startliste = Schwimmer.objects.select_related().filter(disziplin=d).order_by('-creation_date')
    paginator = Paginator(startliste, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "schwimmen_eingabe.html",
            {'wettkampf': d.wettkampf, 'disziplin': d, 'form': form, 'page_obj': page_obj})

@permission_required('sasse.change_gruppe')
def schwimmen_update(request, jahr, wettkampf, startnummer):
    d = _get_spezialwettkampf(jahr, wettkampf, "Schwimmen")
    schwimmer = Schwimmer.objects.get(disziplin=d, startnummer=startnummer)
    if request.method == 'POST':
        form = SchwimmerUpdateForm(request.POST.copy(), instance=schwimmer)
        if form.is_valid():
            form.save()
            url = reverse(schwimmen_eingabe, args=[jahr, wettkampf])
            return HttpResponseRedirect(url)
    else:
        form = SchwimmerUpdateForm(instance=schwimmer)
    return render(request, "schwimmen_update.html",
            {'wettkampf': d.wettkampf, 'disziplin': d, 'form': form})

@permission_required('sasse.change_gruppe')
def schwimmen_delete(request, jahr, wettkampf, startnummer):
    d = _get_spezialwettkampf(jahr, wettkampf, "Schwimmen")
    schwimmer = Schwimmer.objects.get(disziplin=d, startnummer=startnummer)
    if request.method == 'POST':
        schwimmer.delete()
        url = reverse(schwimmen_eingabe, args=[jahr, wettkampf])
        return HttpResponseRedirect(url)
    return render(request, "schwimmen_delete.html",
            {'wettkampf': d.wettkampf, 'disziplin': d, 'obj': schwimmer})

def schwimmen_rangliste(request, jahr, wettkampf, kategorie=None):
    assert request.method == 'GET'
    d = _get_spezialwettkampf(jahr, wettkampf, "Schwimmen")
    gestartete_kategorien = list(read_schwimmen_gestartete_kategorien(d))
    aktuelle_kategorie = _get_spezialwettkampf_kat(gestartete_kategorien, kategorie)
    kranzlimite = _get_spezialwettkampf_limite(d, aktuelle_kategorie)
    rangliste = Schwimmer.objects.filter(disziplin=d, kategorie=aktuelle_kategorie).order_by('zeit')
    rangliste, kranz_prozent = _create_spezialwettkampf_rangliste(rangliste, kranzlimite)
    paginator = Paginator(rangliste, 25, orphans=3)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, 'schwimmen_rangliste.html',
            {'wettkampf': d.wettkampf, 'disziplin': d, 'kategorie': aktuelle_kategorie, 'kategorien':
                gestartete_kategorien, 'page_obj': page_obj, 'kranzlimite':
                kranzlimite, 'kranzlimite_in_prozent': kranz_prozent})

def schwimmen_rangliste_pdf(request, jahr, wettkampf, kategorie):
    assert request.method == 'GET'
    d = _get_spezialwettkampf(jahr, wettkampf, "Schwimmen")
    w = d.wettkampf
    flowables = _create_pdf_schwimmen(d, kategorie)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = smart_str('filename=rangliste-%s-kat-%s' % (w.name, kategorie))
    doc = create_rangliste_doctemplate(w)
    doc.build(flowables, filename=response)
    return response

@permission_required('sasse.change_gruppe')
def schwimmen_kranzlimite_update(request, jahr, wettkampf, kategorie):
    d = _get_spezialwettkampf(jahr, wettkampf, "Schwimmen")
    return _do_kranzlimite_update(request, jahr, wettkampf, d, kategorie, schwimmen_rangliste)

#
# Einzelschnüren
#

def einzelschnueren_get(request, jahr, wettkampf):
    return _do_spezialwettkampf_get(request, jahr, wettkampf, "Einzelschnüren")

@permission_required('sasse.change_gruppe')
def einzelschnueren_eingabe(request, jahr, wettkampf):
    d = _get_spezialwettkampf(jahr, wettkampf, "Einzelschnüren")
    if request.method == 'POST':
        form = EinzelschnuererForm(d, request.POST.copy())
        if form.is_valid():
            form.save()
            url = reverse(einzelschnueren_eingabe, args=[jahr, wettkampf])
            return HttpResponseRedirect(url)
    else:
        form = EinzelschnuererForm(d, initial={'zuschlaege': 0})
    startliste = Einzelschnuerer.objects.select_related().filter(disziplin=d).order_by('-creation_date')
    paginator = Paginator(startliste, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "einzelschnueren_eingabe.html",
            {'wettkampf': d.wettkampf, 'disziplin': d, 'form': form, 'page_obj': page_obj})

@permission_required('sasse.change_gruppe')
def einzelschnueren_update(request, jahr, wettkampf, startnummer):
    d = _get_spezialwettkampf(jahr, wettkampf, "Einzelschnüren")
    schnuerer = Einzelschnuerer.objects.get(disziplin=d, startnummer=startnummer)
    if request.method == 'POST':
        form = EinzelschnuererUpdateForm(request.POST.copy(), instance=schnuerer)
        if form.is_valid():
            form.save()
            url = reverse(einzelschnueren_eingabe, args=[jahr, wettkampf])
            return HttpResponseRedirect(url)
    else:
        form = EinzelschnuererUpdateForm(instance=schnuerer)
    return render(request, "einzelschnueren_update.html",
            {'wettkampf': d.wettkampf, 'disziplin': d, 'form': form})

@permission_required('sasse.change_gruppe')
def einzelschnueren_delete(request, jahr, wettkampf, startnummer):
    d = _get_spezialwettkampf(jahr, wettkampf, "Einzelschnüren")
    schnuerer = Einzelschnuerer.objects.get(disziplin=d, startnummer=startnummer)
    if request.method == 'POST':
        schnuerer.delete()
        url = reverse(einzelschnueren_eingabe, args=[jahr, wettkampf])
        return HttpResponseRedirect(url)
    return render(request, "einzelschnueren_delete.html",
            {'wettkampf': d.wettkampf, 'disziplin': d, 'obj': schnuerer})

def einzelschnueren_rangliste(request, jahr, wettkampf, kategorie=None):
    assert request.method == 'GET'
    d = _get_spezialwettkampf(jahr, wettkampf, "Einzelschnüren")
    gestartete_kategorien = list(read_einzelschnueren_gestartete_kategorien(d))
    aktuelle_kategorie = _get_spezialwettkampf_kat(gestartete_kategorien, kategorie)
    kranzlimite = _get_spezialwettkampf_limite(d, aktuelle_kategorie)
    rangliste = Einzelschnuerer.objects.filter(disziplin=d, kategorie=aktuelle_kategorie).order_by('zeit')
    rangliste, kranz_prozent = _create_spezialwettkampf_rangliste(rangliste, kranzlimite)
    paginator = Paginator(rangliste, 25, orphans=3)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, 'einzelschnueren_rangliste.html',
            {'wettkampf': d.wettkampf, 'disziplin': d, 'kategorie': aktuelle_kategorie, 'kategorien':
                gestartete_kategorien, 'page_obj': page_obj, 'kranzlimite':
                kranzlimite, 'kranzlimite_in_prozent': kranz_prozent})

def einzelschnueren_rangliste_pdf(request, jahr, wettkampf, kategorie):
    assert request.method == 'GET'
    d = _get_spezialwettkampf(jahr, wettkampf, "Einzelschnüren")
    w = d.wettkampf
    flowables = _create_pdf_einzelschnueren(d, kategorie)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = smart_str('filename=rangliste-%s-kat-%s' % (w.name, kategorie))
    doc = create_rangliste_doctemplate(w)
    doc.build(flowables, filename=response)
    return response

@permission_required('sasse.change_gruppe')
def einzelschnueren_kranzlimite_update(request, jahr, wettkampf, kategorie):
    d = _get_spezialwettkampf(jahr, wettkampf, "Einzelschnüren")
    return _do_kranzlimite_update(request, jahr, wettkampf, d, kategorie, einzelschnueren_rangliste)

#
# Gruppenschnüren
#

def gruppenschnueren_get(request, jahr, wettkampf):
    return _do_spezialwettkampf_get(request, jahr, wettkampf, "Gruppenschnüren")

@permission_required('sasse.change_gruppe')
def gruppenschnueren_eingabe(request, jahr, wettkampf):
    d = _get_spezialwettkampf(jahr, wettkampf, "Gruppenschnüren")
    if request.method == 'POST':
        form = SchnuergruppeForm(d, request.POST.copy())
        if form.is_valid():
            form.save()
            url = reverse(gruppenschnueren_eingabe, args=[jahr, wettkampf])
            return HttpResponseRedirect(url)
    else:
        form = SchnuergruppeForm(d, initial={'zuschlaege': 0})
    startliste = Schnuergruppe.objects.select_related().filter(disziplin=d).order_by('-creation_date')
    return render(request, "gruppenschnueren_eingabe.html",
            {'wettkampf': d.wettkampf, 'disziplin': d, 'form': form, 'startliste': startliste})

@permission_required('sasse.change_gruppe')
def gruppenschnueren_update(request, jahr, wettkampf, startnummer):
    d = _get_spezialwettkampf(jahr, wettkampf, "Gruppenschnüren")
    gruppe = Schnuergruppe.objects.get(disziplin=d, startnummer=startnummer)
    if request.method == 'POST':
        form = SchnuergruppeUpdateForm(request.POST.copy(), instance=gruppe)
        if form.is_valid():
            form.save()
            url = reverse(gruppenschnueren_eingabe, args=[jahr, wettkampf])
            return HttpResponseRedirect(url)
    else:
        form = SchnuergruppeUpdateForm(instance=gruppe)
    return render(request, "gruppenschnueren_update.html",
            {'wettkampf': d.wettkampf, 'disziplin': d, 'form': form})

@permission_required('sasse.change_gruppe')
def gruppenschnueren_delete(request, jahr, wettkampf, startnummer):
    d = _get_spezialwettkampf(jahr, wettkampf, "Gruppenschnüren")
    gruppe = Schnuergruppe.objects.get(disziplin=d, startnummer=startnummer)
    if request.method == 'POST':
        gruppe.delete()
        url = reverse(gruppenschnueren_eingabe, args=[jahr, wettkampf])
        return HttpResponseRedirect(url)
    return render(request, "gruppenschnueren_delete.html",
            {'wettkampf': d.wettkampf, 'disziplin': d, 'obj': gruppe})

def gruppenschnueren_rangliste(request, jahr, wettkampf, kategorie=None):
    assert request.method == 'GET'
    d = _get_spezialwettkampf(jahr, wettkampf, "Gruppenschnüren")
    gestartete_kategorien = list(read_gruppenschnueren_gestartete_kategorien(d))
    aktuelle_kategorie = _get_spezialwettkampf_kat(gestartete_kategorien, kategorie)
    kranzlimite = _get_spezialwettkampf_limite(d, aktuelle_kategorie)
    rangliste = Schnuergruppe.objects.filter(disziplin=d, kategorie=aktuelle_kategorie).order_by('zeit')
    rangliste, kranz_prozent = _create_spezialwettkampf_rangliste(rangliste, kranzlimite)
    return render(request, 'gruppenschnueren_rangliste.html',
            {'wettkampf': d.wettkampf, 'disziplin': d, 'kategorie': aktuelle_kategorie, 'kategorien':
                gestartete_kategorien, 'rangliste': rangliste, 'kranzlimite':
                kranzlimite, 'kranzlimite_in_prozent': kranz_prozent})

def gruppenschnueren_rangliste_pdf(request, jahr, wettkampf, kategorie):
    assert request.method == 'GET'
    d = _get_spezialwettkampf(jahr, wettkampf, "Gruppenschnüren")
    w = d.wettkampf
    flowables = _create_pdf_gruppenschnueren(d, kategorie)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = smart_str('filename=rangliste-%s-kat-%s' % (w.name, kategorie))
    doc = create_rangliste_doctemplate(w)
    doc.build(flowables, filename=response)
    return response

@permission_required('sasse.change_gruppe')
def gruppenschnueren_kranzlimite_update(request, jahr, wettkampf, kategorie):
    d = _get_spezialwettkampf(jahr, wettkampf, "Gruppenschnüren")
    return _do_kranzlimite_update(request, jahr, wettkampf, d, kategorie, gruppenschnueren_rangliste)

#
# Bootfaehrengruppe
#

def bootfaehrenbau_get(request, jahr, wettkampf):
    return _do_spezialwettkampf_get(request, jahr, wettkampf, "Bootsfährenbau")

@permission_required('sasse.change_gruppe')
def bootfaehrenbau_eingabe(request, jahr, wettkampf):
    d = _get_spezialwettkampf(jahr, wettkampf, "Bootsfährenbau")
    if request.method == 'POST':
        form = BootfaehrengruppeForm(d, request.POST.copy())
        if form.is_valid():
            form.save()
            url = reverse(bootfaehrenbau_eingabe, args=[jahr, wettkampf])
            return HttpResponseRedirect(url)
    else:
        form = BootfaehrengruppeForm(d, initial={'zuschlaege': 0})
    startliste = Bootfaehrengruppe.objects.select_related().filter(disziplin=d).order_by('-creation_date')
    return render(request, "bootfaehrenbau_eingabe.html",
            {'wettkampf': d.wettkampf, 'disziplin': d, 'form': form, 'startliste': startliste})

@permission_required('sasse.change_gruppe')
def bootfaehrenbau_update(request, jahr, wettkampf, startnummer):
    d = _get_spezialwettkampf(jahr, wettkampf, "Bootsfährenbau")
    gruppe = Bootfaehrengruppe.objects.get(disziplin=d, startnummer=startnummer)
    if request.method == 'POST':
        form = BootfaehrengruppeUpdateForm(request.POST.copy(), instance=gruppe)
        if form.is_valid():
            form.save()
            url = reverse(bootfaehrenbau_eingabe, args=[jahr, wettkampf])
            return HttpResponseRedirect(url)
    else:
        form = BootfaehrengruppeUpdateForm(instance=gruppe)
    return render(request, "bootfaehrenbau_update.html",
            {'wettkampf': d.wettkampf, 'disziplin': d, 'form': form})

@permission_required('sasse.change_gruppe')
def bootfaehrenbau_delete(request, jahr, wettkampf, startnummer):
    d = _get_spezialwettkampf(jahr, wettkampf, "Bootsfährenbau")
    gruppe = Bootfaehrengruppe.objects.get(disziplin=d, startnummer=startnummer)
    if request.method == 'POST':
        gruppe.delete()
        url = reverse(bootfaehrenbau_eingabe, args=[jahr, wettkampf])
        return HttpResponseRedirect(url)
    return render(request, "bootfaehrenbau_delete.html",
            {'wettkampf': d.wettkampf, 'disziplin': d, 'obj': gruppe})

def bootfaehrenbau_rangliste(request, jahr, wettkampf, kategorie=None):
    assert request.method == 'GET'
    d = _get_spezialwettkampf(jahr, wettkampf, "Bootsfährenbau")
    gestartete_kategorien = list(read_bootfaehrenbau_gestartete_kategorien(d))
    aktuelle_kategorie = _get_spezialwettkampf_kat(gestartete_kategorien, kategorie)
    kranzlimite = _get_spezialwettkampf_limite(d, aktuelle_kategorie)
    rangliste = Bootfaehrengruppe.objects.filter(disziplin=d, kategorie=aktuelle_kategorie).order_by('zeit')
    rangliste, kranz_prozent = _create_spezialwettkampf_rangliste(rangliste, kranzlimite)
    return render(request, 'bootfaehrenbau_rangliste.html',
            {'wettkampf': d.wettkampf, 'disziplin': d, 'kategorie': aktuelle_kategorie, 'kategorien':
                gestartete_kategorien, 'rangliste': rangliste, 'kranzlimite':
                kranzlimite, 'kranzlimite_in_prozent': kranz_prozent})

def bootfaehrenbau_rangliste_pdf(request, jahr, wettkampf, kategorie):
    assert request.method == 'GET'
    d = _get_spezialwettkampf(jahr, wettkampf, "Bootsfährenbau")
    w = d.wettkampf
    flowables = _create_pdf_bootfaehrenbau(d, kategorie)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = smart_str('filename=rangliste-%s-kat-%s' % (w.name, kategorie))
    doc = create_rangliste_doctemplate(w)
    doc.build(flowables, filename=response)
    return response

@permission_required('sasse.change_gruppe')
def bootfaehrenbau_kranzlimite_update(request, jahr, wettkampf, kategorie):
    d = _get_spezialwettkampf(jahr, wettkampf, "Bootsfährenbau")
    return _do_kranzlimite_update(request, jahr, wettkampf, d, kategorie, bootfaehrenbau_rangliste)

#
# Generationenpaar
#

def generationenpaar_get(request, jahr, wettkampf):
    return _do_spezialwettkampf_get(request, jahr, wettkampf, "Generationenpaar")

@permission_required('sasse.change_gruppe')
def generationenpaar_eingabe(request, jahr, wettkampf):
    d = _get_spezialwettkampf(jahr, wettkampf, "Generationenpaar")
    if request.method == 'POST':
        form = GenerationenpaarForm(d, request.POST.copy())
        if form.is_valid():
            form.save()
            url = reverse(generationenpaar_eingabe, args=[jahr, wettkampf])
            return HttpResponseRedirect(url)
    else:
        form = GenerationenpaarForm(d)
    startliste = Generationenpaar.objects.select_related().filter(disziplin=d).order_by('-creation_date')
    paginator = Paginator(startliste, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "generationenpaar_eingabe.html",
            {'wettkampf': d.wettkampf, 'disziplin': d, 'form': form, 'page_obj': page_obj})

@permission_required('sasse.change_gruppe')
def generationenpaar_update(request, jahr, wettkampf, startnummer):
    d = _get_spezialwettkampf(jahr, wettkampf, "Generationenpaar")
    paar = Generationenpaar.objects.get(disziplin=d, startnummer=startnummer)
    if request.method == 'POST':
        form = GenerationenpaarUpdateForm(request.POST.copy(), instance=paar)
        if form.is_valid():
            form.save()
            url = reverse(generationenpaar_eingabe, args=[jahr, wettkampf])
            return HttpResponseRedirect(url)
    else:
        form = GenerationenpaarUpdateForm(instance=paar)
    return render(request, "generationenpaar_update.html",
            {'wettkampf': d.wettkampf, 'disziplin': d, 'form': form})

@permission_required('sasse.change_gruppe')
def generationenpaar_delete(request, jahr, wettkampf, startnummer):
    d = _get_spezialwettkampf(jahr, wettkampf, "Generationenpaar")
    paar = Generationenpaar.objects.get(disziplin=d, startnummer=startnummer)
    if request.method == 'POST':
        paar.delete()
        url = reverse(generationenpaar_eingabe, args=[jahr, wettkampf])
        return HttpResponseRedirect(url)
    return render(request, "generationenpaar_delete.html",
            {'wettkampf': d.wettkampf, 'disziplin': d, 'obj': paar})

def generationenpaar_rangliste(request, jahr, wettkampf):
    assert request.method == 'GET'
    d = _get_spezialwettkampf(jahr, wettkampf, "Generationenpaar")
    w = d.wettkampf
    rangliste = read_beste_generationenpaare(w, d)
    paginator = Paginator(rangliste, 26, orphans=2)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, 'generationenpaar_rangliste.html',
            {'wettkampf': d.wettkampf, 'disziplin': d, 'page_obj': page_obj})

def generationenpaar_rangliste_pdf(request, jahr, wettkampf):
    assert request.method == 'GET'
    d = _get_spezialwettkampf(jahr, wettkampf, "Generationenpaar")
    w = d.wettkampf
    flowables = _create_pdf_generationenpaar(d)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = smart_str('filename=generationenpaar-%s' % w.name)
    doc = create_rangliste_doctemplate(w)
    doc.build(flowables, filename=response)
    return response

#
# Hilfsfunktion fuer Ranglisten PDF
#

def _create_pdf_einzelfahren(disziplin, kategorie):
    kranzlimite = read_kranzlimite(disziplin, kategorie)
    rangliste = read_rangliste(disziplin, kategorie)
    rangliste_sorted = sorted(rangliste, key=sort_rangliste)
    return create_rangliste_flowables(rangliste_sorted, kranzlimite, disziplin, kategorie)

def _create_pdf_bestzeiten(disziplin):
    all_ranglisten = []
    zeitposten = disziplin.posten_set.filter(postenart__name='Zeitnote')
    for p in zeitposten:
        zeitrangliste = read_topzeiten(p, 10)
        all_ranglisten.append((p.name, zeitrangliste))
    return create_bestzeiten_flowables(all_ranglisten, disziplin)

def _create_pdf_sektionsfahren(disziplin):
    rangliste = read_sektionsfahren_rangliste(disziplin)
    return create_sektionsfahren_rangliste_flowables(rangliste, disziplin)

def _create_pdf_einzelschnueren(disziplin, kategorie):
    kranzlimite = _get_spezialwettkampf_limite(disziplin, kategorie)
    rangliste = Einzelschnuerer.objects.filter(disziplin=disziplin, kategorie=kategorie).order_by('zeit')
    rangliste, kranz_prozent = _create_spezialwettkampf_rangliste(rangliste, kranzlimite)
    return create_einzelschnueren_rangliste_flowables(rangliste, kranzlimite, disziplin, kategorie)

def _create_pdf_gruppenschnueren(disziplin, kategorie):
    kranzlimite = _get_spezialwettkampf_limite(disziplin, kategorie)
    rangliste = Schnuergruppe.objects.filter(disziplin=disziplin, kategorie=kategorie).order_by('zeit')
    rangliste, kranz_prozent = _create_spezialwettkampf_rangliste(rangliste, kranzlimite)
    return create_gruppenschnueren_rangliste_flowables(rangliste, kranzlimite, disziplin, kategorie)

def _create_pdf_bootfaehrenbau(disziplin, kategorie):
    kranzlimite = _get_spezialwettkampf_limite(disziplin, kategorie)
    rangliste = Bootfaehrengruppe.objects.filter(disziplin=disziplin, kategorie=kategorie).order_by('zeit')
    rangliste, kranz_prozent = _create_spezialwettkampf_rangliste(rangliste, kranzlimite)
    return create_bootfaehrenbau_rangliste_flowables(rangliste, kranzlimite, disziplin)

def _create_pdf_schwimmen(disziplin, kategorie):
    kranzlimite = _get_spezialwettkampf_limite(disziplin, kategorie)
    rangliste = Schwimmer.objects.filter(disziplin=disziplin, kategorie=kategorie).order_by('zeit')
    rangliste, kranz_prozent = _create_spezialwettkampf_rangliste(rangliste, kranzlimite)
    return create_schwimmen_rangliste_flowables(rangliste, kranzlimite, disziplin, kategorie)


#
# Rangliste über ganzen Wettkampf
#

def rangliste_komplett_pdf(request, jahr, wettkampf):

    def sort_by_disziplinart(d):
        if d.disziplinart.name == "Sektionsfahren":
            return 1
        elif d.disziplinart.name == "Einzelfahren":
            if d.kategorien.filter(name = "I").exists():
                return 2
            else:
                return 3
        elif d.disziplinart.name == "Einzelschnüren":
            return 4
        elif d.disziplinart.name == "Gruppenschnüren":
            return 5
        elif d.disziplinart.name == "Bootsfährenbau":
            return 6
        elif d.disziplinart.name == "Schwimmen":
            return 7
        else:
            return 8

    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    doc = create_rangliste_doctemplate(w)
    flowables = []
    for d in sorted(w.disziplin_set.all(), key = sort_by_disziplinart):
        if d.disziplinart.name == "Sektionsfahren":
            flowables.extend(_create_pdf_sektionsfahren(d))
        elif d.disziplinart.name == "Einzelfahren":
            for k in read_startende_kategorien(d):
                flowables.extend(_create_pdf_einzelfahren(d, k))
            flowables.extend(_create_pdf_bestzeiten(d))
        elif d.disziplinart.name == "Einzelschnüren":
            for k in read_einzelschnueren_gestartete_kategorien(d):
                flowables.extend(_create_pdf_einzelschnueren(d, k))
        elif d.disziplinart.name == "Gruppenschnüren":
            for k in read_gruppenschnueren_gestartete_kategorien(d):
                flowables.extend(_create_pdf_gruppenschnueren(d, k))
        elif d.disziplinart.name == "Bootsfährenbau":
            flowables.extend(_create_pdf_bootfaehrenbau(d, 'Aktive'))
        elif d.disziplinart.name == "Schwimmen":
            for k in read_schwimmen_gestartete_kategorien(d):
                flowables.extend(_create_pdf_schwimmen(d, k))
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = smart_str('filename=rangliste-komplett-%s' % w.name)
    doc.build(flowables, filename=response)
    return response

