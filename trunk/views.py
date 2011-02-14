# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.forms.formsets import all_valid
from django.template import RequestContext
from django.forms.formsets import formset_factory

from models import Wettkampf
from models import Disziplin
from models import Disziplinart
from models import Posten
from models import Teilnehmer
from models import Schiffeinzel
from models import Richtzeit
from models import Sektion
from models import Kranzlimite

from forms import DisziplinForm
from forms import PostenEditForm
from forms import PostenListForm
from forms import SchiffeinzelEditForm
from forms import SchiffeinzelListForm
from forms import SchiffeinzelFilterForm
from forms import PostenblattFilterForm
from forms import TeilnehmerForm
from forms import WettkampfForm
from forms import create_postenblatt_formsets
from forms import RichtzeitForm
from forms import KranzlimiteForm

from queries import read_topzeiten
from queries import read_notenliste
from queries import read_notenblatt
from queries import read_kranzlimite
from queries import read_kranzlimiten
from queries import read_rangliste
from queries import sort_rangliste
from queries import read_startende_kategorien

from reports import create_rangliste_doctemplate
from reports import create_rangliste_flowables


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
    return render_to_response('wettkampf_add.html', {'form': form})

def wettkaempfe_post(request):
    assert request.method == 'POST'
    form = WettkampfForm(request.POST)
    if form.is_valid():
        w = form.save()
        url = reverse(wettkampf_get, args=[w.jahr(), w.name])
        return HttpResponseRedirect(url)
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
        w = form.save()
        url = reverse(wettkampf_get, args=[w.jahr(), w.name])
        return HttpResponseRedirect(url)
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
    form = DisziplinForm(w)
    return render_to_response('disziplin_add.html',
            {'form': form, 'wettkampf': w})

def disziplinen_post(request, jahr, wettkampf):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    form = DisziplinForm(w, request.POST.copy())
    if form.is_valid():
        form.save()
        url = reverse(wettkampf_get, args=[jahr, wettkampf])
        return HttpResponseRedirect(url)
    return render_to_response('disziplin_add.html',
            {'form': form, 'wettkampf': w})

def disziplin_get(request, jahr, wettkampf, disziplin):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    template = None
    if d.disziplinart == Disziplinart.objects.get(name="Einzelfahren"):
        template = "einzelfahren.html"
    elif d.disziplinart == Disziplinart.objects.get(name="Sektionsfahren"):
        template = "einzelfahren.html"
    else:
        raise Http404(u"Disziplin %s noch nicht implementiert" % d.disziplinart)
    return render_to_response(template, {'wettkampf': w, 'disziplin': d})

def disziplin_update(request, jahr, wettkampf, disziplin):
    if request.method == 'POST':
        return disziplin_put(request, jahr, wettkampf, disziplin)
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    form = DisziplinForm(w, instance=d)
    return render_to_response('disziplin_update.html',
            {'form': form, 'wettkampf': w, 'disziplin': d})

def disziplin_put(request, jahr, wettkampf, disziplin):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    form = DisziplinForm(w, request.POST.copy(), instance=d)
    if form.is_valid():
        d = form.save()
        url = reverse(disziplin_get, args=[jahr, wettkampf, d.name])
        return HttpResponseRedirect(url)
    return render_to_response('disziplin_update.html',
            {'form': form, 'wettkampf': w, 'disziplin': d})

def disziplin_delete_confirm(request, jahr, wettkampf, disziplin):
    if request.method == 'POST':
        return disziplin_delete(request, jahr, wettkampf, disziplin)
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    return render_to_response('disziplin_delete.html',
            {'wettkampf': w, 'disziplin': d})

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
    return render_to_response('posten.html',
        {'wettkampf': w, 'disziplin': d, 'posten': d.posten_set.all(),
            'form': form, })

def posten_post(request, jahr, wettkampf, disziplin):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    form = PostenListForm(d, request.POST.copy())
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(posten_list, args=[jahr, wettkampf, disziplin]))
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
    form = PostenEditForm(d, instance=p)
    return render_to_response('posten_update.html',
            {'form': form, 'wettkampf': w, 'disziplin': d, 'posten': p, })

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

def startliste(request, jahr, wettkampf, disziplin):
    if request.method == 'POST':
        return startliste_post(request, jahr, wettkampf, disziplin)
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    if d.disziplinart == Disziplinart.objects.get(name="Einzelfahren"):
        return startliste_einzelfahren(request, jahr, wettkampf, disziplin)
    else:
        raise Http404(u"Startliste für %s noch nicht implementiert"
                % d.disziplinart)

def startliste_post(request, jahr, wettkampf, disziplin):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    if d.disziplinart == Disziplinart.objects.get(name="Einzelfahren"):
        return startliste_einzelfahren_post(request, jahr, wettkampf, disziplin)
    else:
        raise Http404(u"Mutieren der Startliste für %s noch nicht implementiert"
                % d.disziplinart)

def startliste_einzelfahren(request, jahr, wettkampf, disziplin):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    s = []
    entryform = None
    searchform = SchiffeinzelFilterForm(d, request.GET)
    if searchform.is_valid():
        s = searchform.anzeigeliste()
        nummer = searchform.naechste_nummer(s)
        entryform = SchiffeinzelListForm(d, initial={'startnummer': nummer})
    return render_to_response('startliste_einzelfahren.html', {
        'wettkampf': w, 'disziplin': d, 'searchform': searchform,
        'startliste': s, 'form': entryform},
        context_instance=RequestContext(request)
        )

def startliste_einzelfahren_post(request, jahr, wettkampf, disziplin):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    entryform = SchiffeinzelListForm(d, request.POST.copy())
    if entryform.is_valid():
        entryform.save()
        url = reverse(startliste, args=[jahr, wettkampf, disziplin])
        query = request.META.get('QUERY_STRING')
        if query:
            url = "%s?%s" % (url, query)
        return HttpResponseRedirect(url)
    searchform = SchiffeinzelFilterForm(d, request.GET)
    if searchform.is_valid():
        s = searchform.anzeigeliste()
    return render_to_response('startliste_einzelfahren.html', {
        'wettkampf': w, 'disziplin': d, 'searchform': searchform,
        'startliste': s, 'form': entryform},
        context_instance=RequestContext(request)
        )

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
        'steuermann': t.steuermann.get_edit_text(),
        'vorderfahrer': t.vorderfahrer.get_edit_text(),
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
        args = [jahr, wettkampf, disziplin, startnummer]
        url = reverse(teilnehmer_get, args=args)
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

def bewertungen(request, jahr, wettkampf, disziplin):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    if d.posten_set.count() == 0:
        raise Http404(u"Es sind noch keine Posten definiert")
    p = d.posten_set.all()[0]
    url = reverse(postenblatt, args=[jahr, wettkampf, disziplin, p.name])
    return HttpResponseRedirect(url)

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
    filterform = PostenblattFilterForm(d, request.GET)
    if filterform.is_valid():
        startnummern = filterform.selected_startnummern(visible=15)
        teilnehmer_ids = [t.id for t in startnummern]
        sets = create_postenblatt_formsets(p, teilnehmer_ids)
        header_row, data_rows = create_postenblatt_table(startnummern, sets, orientation)
    return render_to_response('postenblatt.html', {'wettkampf': w, 'disziplin':
        d, 'posten': p, 'filterform': filterform, 'header_row': header_row,
        'data_rows': data_rows, 'query': query,})

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
    filterform = PostenblattFilterForm(d, request.GET)
    if filterform.is_valid():
        startnummern = filterform.selected_startnummern(visible=15)
        TeilnehmerFormSet = formset_factory(TeilnehmerForm, extra=0)
        initial = [{'id': t.id, 'startnummer': t.startnummer} for t in startnummern]
        teilnehmer_formset = TeilnehmerFormSet(initial=initial, prefix='stnr')
        teilnehmer_ids = [t.id for t in startnummern]
        sets = create_postenblatt_formsets(p, teilnehmer_ids)
        orientation = get_orientation(p, request)
        header_row, data_rows = create_postenblatt_table(startnummern, sets, orientation)
        p_next_list = list(d.posten_set.filter(reihenfolge__gt=p.reihenfolge))
        if p_next_list:
            p_next_name = p_next_list[0].name
    return render_to_response("postenblatt_update.html", {'wettkampf': w,
        'disziplin': d, 'posten': p, 'teilnehmer_formset': teilnehmer_formset,
        'formset': sets, 'header_row': header_row, 'data_rows': data_rows,
        'posten_next_name': p_next_name})

def postenblatt_post(request, jahr, wettkampf, disziplin, posten):
    assert request.method == 'POST'
    p = Posten.objects.select_related().get(
            name=posten,
            disziplin__name=disziplin,
            disziplin__wettkampf__name=wettkampf,
            disziplin__wettkampf__von__year=jahr)
    d = p.disziplin
    w = d.wettkampf
    p_next_name = request.POST.get('posten_next_name')
    TeilnehmerFormSet = formset_factory(TeilnehmerForm)
    teilnehmer_formset = TeilnehmerFormSet(data=request.POST, prefix='stnr')
    if not teilnehmer_formset.is_valid():
        # Sollte nicht passieren
        raise Exception(u"%s" % teilnehmer_formset.errors)
    teilnehmer_ids = [f.cleaned_data['id'] for f in teilnehmer_formset.forms]
    sets = create_postenblatt_formsets(p, teilnehmer_ids, data=request.POST)
    if all_valid(sets):
        for formset in sets:
            formset.save()
        view = postenblatt
        if request.POST.has_key('save_and_next'):
            posten = p_next_name
            view = postenblatt_update
        elif request.POST.has_key('save_and_finish'):
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
    return render_to_response('postenblatt_update.html', {'wettkampf': w,
        'disziplin': d, 'posten': p, 'teilnehmer_formset': teilnehmer_formset,
        'formset': sets, 'header_row': header_row, 'data_rows': data_rows,
        'posten_next_name': p_next_name})

def get_orientation(posten, request):
    orientation = 'HORIZONTAL'
    if posten.postenart.name == 'Zeitnote':
        orientation = 'VERTIKAL'
    if request.GET.has_key('o'):
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
            next_cells = [set.forms[k] for k in range(len(startnummern))]
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
        raise Http404(u"Es gibt gar keine Zeitposten")
    p = zeitposten[0]
    url = reverse(richtzeit, args=[jahr, wettkampf, disziplin, p.name])
    return HttpResponseRedirect(url)

def richtzeit(request, jahr, wettkampf, disziplin, posten, template='richtzeit.html'):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    p = Posten.objects.get(disziplin=d, name=posten)
    form = RichtzeitForm(p)
    zeitposten = d.posten_set.filter(postenart__name='Zeitnote')
    rangliste = read_topzeiten(p)
    return render_to_response(template, {'wettkampf': w, 'disziplin':
        d, 'posten': p, 'zeitposten': zeitposten, 'rangliste': rangliste,
        'form': form})

def richtzeit_update(request, jahr, wettkampf, disziplin, posten):
    if request.method == 'POST':
        return richtzeit_post(request, jahr, wettkampf, disziplin, posten)
    return richtzeit(request, jahr, wettkampf, disziplin, posten, 'richtzeit_update.html')

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
    rangliste = read_topzeiten(p)
    return render_to_response('richtzeit_update.html', {'wettkampf': w,
        'disziplin': d, 'posten': p, 'zeitposten': zeitposten, 'rangliste':
        rangliste, 'form': form})

def notenliste(request, jahr, wettkampf, disziplin):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    posten = d.posten_set.all().select_related()
    sektion = None
    filter_form = SchiffeinzelFilterForm(d, request.GET.copy())
    if filter_form.is_valid():
        sektion = filter_form.cleaned_data['sektion']
    notenliste = read_notenliste(d, posten, sektion)
    return render_to_response('notenliste.html', {'wettkampf': w, 'disziplin':
        d, 'posten': posten, 'notenliste': list(notenliste), 'searchform': filter_form},
        context_instance=RequestContext(request))

def rangliste(request, jahr, wettkampf, disziplin, kategorie=None):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    if kategorie:
        k = d.kategorien.get(name=kategorie)
    else:
        k = d.kategorien.all()[0]
    kranzlimite = read_kranzlimite(d, k)
    rangliste = read_rangliste(d, k)
    rangliste_sorted = sorted(rangliste, key=sort_rangliste)
    return render_to_response('rangliste.html', {'wettkampf': w, 'disziplin':
        d, 'kategorie': k, 'rangliste': rangliste_sorted,
        'kranzlimite': kranzlimite}, context_instance=RequestContext(request))

def rangliste_pdf(request, jahr, wettkampf, disziplin, kategorie):
    #return rangliste_pdf_all(request, jahr, wettkampf, disziplin)
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    k = d.kategorien.get(name=kategorie)
    rangliste = read_rangliste(d, k)
    rangliste_sorted = sorted(rangliste, key=sort_rangliste)
    doc = create_rangliste_doctemplate(w, d)
    flowables = create_rangliste_flowables(rangliste_sorted, k)
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'filename=%s' % "rangliste-%s.pdf" % d.name
    doc.build(flowables, filename=response)
    return response

def rangliste_pdf_all(request, jahr, wettkampf, disziplin):
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'filename=%s' % "rangliste-%s.pdf" % d.name
    doc = create_rangliste_doctemplate(w, d)
    flowables = []
    #for d in w.disziplin_set.all():
    for k in d.kategorien.all():
        rangliste = read_rangliste(d, k)
        rangliste_sorted = sorted(rangliste, key=sort_rangliste)
        flowables += create_rangliste_flowables(rangliste_sorted, k)
    doc.build(flowables, filename=response)
    return response

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
    return render_to_response('notenblatt.html', {'wettkampf': w, 'disziplin':
        d, 'schiff': s, 'posten_werte': posten_werte, 'next': next},
        context_instance=RequestContext(request))

def kranzlimiten(request, jahr, wettkampf, disziplin):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    kranzlimiten = read_kranzlimiten(d)
    return render_to_response('kranzlimiten.html', {'wettkampf': w,
        'disziplin': d, 'kranzlimiten': kranzlimiten},
        context_instance=RequestContext(request))

def kranzlimiten_update(request, jahr, wettkampf, disziplin):
    if request.method == 'POST':
        return kranzlimiten_put(request, jahr, wettkampf, disziplin)
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    limite_pro_kategorie = {}
    for kl in Kranzlimite.objects.filter(disziplin=d):
        limite_pro_kategorie[kl.kategorie_id] = kl
    initial = []
    for k in read_startende_kategorien(d):
        kl = limite_pro_kategorie.get(k.id)
        if kl is None:
            kl = Kranzlimite(disziplin=d, kategorie=k)
        dict = {'kl_id': kl.id, 'kl_wert': kl.wert, 'kat_id': k.id, 'kat_name': k.name,}
        initial.append(dict)
    KranzlimiteFormSet = formset_factory(KranzlimiteForm, extra=0)
    formset = KranzlimiteFormSet(initial=initial)
    return render_to_response('kranzlimiten_update.html',
            {'wettkampf': w, 'disziplin': d, 'formset': formset})

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
    return render_to_response('kranzlimiten_update.html',
            {'wettkampf': w, 'disziplin': d, 'formset': formset})

#-----------
#    from django.db import connection
#    for q in connection.queries:
#        print "--------"
#        print q
#    print "Anzahl Queries", len(connection.queries)
