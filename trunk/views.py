# -*- coding: utf-8 -*-

from decimal import Decimal

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.shortcuts import render_to_response
from django.forms.formsets import all_valid
from django.template.loader import render_to_string
from django.template import RequestContext
from django.forms.formsets import formset_factory

from models import Wettkampf
from models import Disziplin
from models import Disziplinart
from models import Posten
from models import Teilnehmer
from models import Schiffeinzel
from models import Bewertung
from models import Richtzeit
from models import Sektion
from models import Bewertungsart
from models import Kranzlimite

from forms import DisziplinForm
from forms import PostenEditForm
from forms import PostenListForm
from forms import SchiffeinzelEditForm
from forms import SchiffeinzelListForm
from forms import SchiffeinzelFilterForm
from forms import PostenblattFilterForm
from forms import TeilnehmerContainerForm
from forms import WettkampfForm
from forms import create_postenblatt_formsets
from forms import RichtzeitForm
from forms import KranzlimiteForm


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

def postenblatt(request, jahr, wettkampf, disziplin, posten, template="postenblatt.html"):
    assert request.method == 'GET'
    p = Posten.objects.select_related().get(
            name=posten,
            disziplin__name=disziplin,
            disziplin__wettkampf__name=wettkampf,
            disziplin__wettkampf__von__year=jahr)
    d = p.disziplin
    w = d.wettkampf
    query = request.META.get('QUERY_STRING')
    sl = None
    sets = []
    filterform = PostenblattFilterForm(d, request.GET)
    if filterform.is_valid():
        s = filterform.selected_startnummern(visible=15)
        if len(s) > 0:
            sl = TeilnehmerContainerForm(startliste=s)
            sets = create_postenblatt_formsets(posten=p, startliste=s)
    try:
        p_next = d.posten_set.filter(reihenfolge__gt=p.reihenfolge)[0]
        p_next_name = p_next.name
    except IndexError:
        # Aktueller Posten ist der Letzte in der Postenliste
        p_next_name = None
    return render_to_response(template, {'wettkampf': w, 'disziplin':
        d, 'posten': p, 'startliste': sl, 'filterform': filterform, 'formset':
        sets, 'query': query, 'posten_next_name': p_next_name })

def postenblatt_update(request, jahr, wettkampf, disziplin, posten):
    if request.method == 'POST':
        return postenblatt_post(request, jahr, wettkampf, disziplin, posten)
    return postenblatt(request, jahr, wettkampf, disziplin, posten, "postenblatt_update.html")

def postenblatt_post(request, jahr, wettkampf, disziplin, posten):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    p = Posten.objects.get(disziplin=d, name=posten)
    p_next_name = request.POST.get('posten_next_name')
    sets = create_postenblatt_formsets(posten=p, data=request.POST)
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
    filterform = PostenblattFilterForm(d, request.GET)
    filterform.is_valid()
    s = filterform.selected_startnummern(visible=15)
    sl = TeilnehmerContainerForm(startliste=s)
    return render_to_response('postenblatt_update.html', {'wettkampf': w,
        'disziplin': d, 'posten': p, 'startliste': sl, 'filterform': filterform,
        'formset': sets, 'posten_next_name': p_next_name})

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

def read_topzeiten(posten, topn=10):
    """
    Bis jetzt habe ich nicht rausgefunden, wie ich 'Schiffeinzel' Objekte (eine
    Subklasse von 'Teilnehmer') zusammen mit den Topzeiten in *einem* SQL
    Select auszulesen kann. 
    """
    result = Bewertung.objects.filter(posten=posten).order_by('zeit')
    result = result.select_related()[:topn]
    teilnehmer_ids = [z.teilnehmer_id for z in result]
    schiffe = Schiffeinzel.objects.select_related().in_bulk(teilnehmer_ids)
    for z in result:
        z.schiff = schiffe[z.teilnehmer_id]
    return result

def notenliste(request, jahr, wettkampf, disziplin):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    posten = d.posten_set.all().select_related()
    sektion = None
    filter_form = SchiffeinzelFilterForm(d, request.GET.copy())
    if filter_form.is_valid():
        sektion = filter_form.cleaned_data['sektion']
        if sektion is None:
            q = Schiffeinzel.objects.all().order_by('sektion')[:1]
            if q.count() > 0:
                sektion = q[0].sektion
                filter_form.data['sektion'] = sektion.id
    list = read_notenliste(d, posten, sektion)
    return render_to_response('notenliste.html', {'wettkampf': w, 'disziplin':
        d, 'posten': posten, 'notenliste': list, 'searchform': filter_form})

def rangliste(request, jahr, wettkampf, disziplin, kategorie=None):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    if kategorie:
        k = d.kategorien.get(name=kategorie)
    else:
        k = d.kategorien.all()[0]
    kranzlimite = read_kranzlimite(d, k)
    rangliste = read_rangliste(d, k, kranzlimite=kranzlimite)
    list = sorted(rangliste, key=sort_rangliste)
    return render_to_response('rangliste.html', {'wettkampf': w, 'disziplin':
        d, 'kategorie': k, 'rangliste': list, 'kranzlimite': kranzlimite},
        context_instance=RequestContext(request))

def notenblatt(request, jahr, wettkampf, disziplin, startnummer=None):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    if startnummer:
        s = Schiffeinzel.objects.select_related().get(disziplin=d, startnummer=startnummer)
    else:
        s = Schiffeinzel.objects.select_related().filter(disziplin=d)[0]
    posten_werte = read_notenblatt(d, s)
    return render_to_response('notenblatt.html', {'wettkampf': w, 'disziplin':
        d, 'schiff': s, 'posten_werte': posten_werte},
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
    kategorien = d.kategorien.all()
    for k in kategorien:
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

def new_bew(col, art):
    """
    Hilfsfunktion, damit ein Bewertung Objekt im Template einfach so verwendet
    werden kann, d.h. eine korrekte String Representation hat.
    """
    wert = Decimal()
    if col:
        wert = Decimal(str(col))
    if art.einheit == 'ZEIT':
        result = Bewertung(zeit=wert, bewertungsart=art)
    else:
        result = Bewertung(note=wert, bewertungsart=art)
    return result

# Hilfskonstanten
ZEIT = Bewertungsart(einheit='ZEIT')
PUNKT = Bewertungsart(einheit='PUNKT')

def read_notenliste(disziplin, posten, sektion=None):
    from django.db import connection
    sql = render_to_string('notenliste.sql',
            {"posten": posten, "sektion": sektion})
    args = [disziplin.id]
    if sektion:
        args.append(sektion.id)
    cursor = connection.cursor()
    cursor.execute(sql, args)
    for row in cursor:
        dict = {}; i = 0
        dict['startnummer'] = row[i]; i += 1
        dict['steuermann'] = row[i]; i += 1
        dict['vorderfahrer'] = row[i]; i += 1
        dict['sektion'] = row[i]; i += 1
        dict['kategorie'] = row[i]; i += 1
        dict['zeit_tot'] = new_bew(row[i], ZEIT); i += 1
        dict['punkt_tot'] = new_bew(row[i], PUNKT); i += 1
        noten = []
        for p in posten:
            if p.postenart.name == "Zeitnote":
                noten.append(new_bew(row[i], ZEIT))
                i += 1
            noten.append(new_bew(row[i], PUNKT))
            i += 1
        dict['noten'] = noten
        yield dict

def read_kranzlimite(disziplin, kategorie):
    result = None
    q = Kranzlimite.objects.filter(disziplin=disziplin, kategorie=kategorie)
    if q.count() > 0:
        result = q[0].wert
    return result

def read_rangliste(disziplin, kategorie, kranzlimite=None,
        doppelstarter_mit_rang=False, letzter_kranzrang=None):
    from django.db import connection
    sql = render_to_string('rangliste.sql')
    args = [disziplin.id, kategorie.id]
    cursor = connection.cursor()
    cursor.execute(sql, args)
    rang = 1
    punkt_tot_prev = None
    zeit_tot_prev = None
    for row in cursor:
        dict = {}; i = 0
        dict['kranz'] = False
        dict['rang'] = None
        dict['doppelstarter'] = False
        dict['startnummer'] = row[i]; i+=1
        dict['steuermann_ist_ds'] = row[i]; i+=1
        dict['vorderfahrer_ist_ds'] = row[i]; i+=1
        dict['steuermann'] = row[i]; i+=1
        dict['vorderfahrer'] = row[i]; i+=1
        dict['sektion'] = row[i]; i += 1
        dict['kategorie'] = row[i]; i += 1
        dict['zeit_tot'] = new_bew(row[i], ZEIT); i += 1
        dict['punkt_tot'] = new_bew(row[i], PUNKT); i += 1
        if (kranzlimite and dict['punkt_tot'].note >= kranzlimite) or (rang <= letzter_kranzrang):
            dict['kranz'] = True
        if dict['steuermann_ist_ds'] or dict['vorderfahrer_ist_ds']:
            dict['doppelstarter'] = True
        if (not dict['doppelstarter']) or doppelstarter_mit_rang:
            dict['rang'] = rang
            if (punkt_tot_prev, zeit_tot_prev) != (dict['punkt_tot'].note, dict['zeit_tot'].zeit):
                rang += 1
        punkt_tot_prev = dict['punkt_tot'].note
        zeit_tot_prev = dict['zeit_tot'].zeit
        yield dict

def sort_rangliste(dict):
    if dict['kranz'] and not dict['doppelstarter']:
        return 1
    if dict['kranz'] and dict['doppelstarter']:
        return 2
    if not dict['kranz'] and not dict['doppelstarter']:
        return 3
    if not dict['kranz'] and dict['doppelstarter']:
        return 4
    return 5

def read_notenblatt(disziplin, teilnehmer=None, sektion=None):
    from django.db import connection
    sql = render_to_string('notenblatt.sql',
            {"teilnehmer": teilnehmer, "sektion": sektion})
    args = [disziplin.id]
    if teilnehmer:
        args.append(teilnehmer.id)
    if sektion:
        args.append(sektion.id)
    cursor = connection.cursor()
    cursor.execute(sql, args)
    zeit_sum = 0
    total_sum = 0
    for row in cursor:
        dict = {}; i = 0
        dict['posten'] = row[i]; i += 1
        dict['posten_art'] = row[i]; i += 1
        dict['abzug'] = new_bew(row[i], PUNKT); i += 1
        dict['note'] = new_bew(row[i], PUNKT); i += 1
        dict['zeit'] = new_bew(row[i], ZEIT); i += 1
        dict['total'] = new_bew(row[i], PUNKT); i += 1
        zeit_sum += dict['zeit'].zeit
        total_sum += dict['total'].note
        if dict['posten_art'] == 'Zeitnote':
            dict['abzug'] = None
            dict['note'] = None
        else:
            dict['zeit'] = None
        yield dict
    dict = {}
    dict['zeit'] = new_bew(zeit_sum, ZEIT)
    dict['total'] = new_bew(total_sum, PUNKT)
    yield dict

def read_kranzlimiten(disziplin):
    from django.db import connection
    sql = render_to_string('kranzlimiten.sql', {"disziplin": disziplin})
    args = [disziplin.id]
    cursor = connection.cursor()
    cursor.execute(sql, args)
    for row in cursor:
        dict = {}; i = 0
        dict['kategorie'] = row[i]; i += 1
        dict['limite_in_punkte'] = new_bew(row[i], PUNKT); i += 1
        dict['limite_in_prozent'] = row[i]; i += 1
        dict['anzahl_raenge'] = row[i]; i += 1
        dict['anzahl_raenge_ueber_limite'] = row[i]; i += 1
        dict['doppelstarter'] = row[i]; i += 1
        dict['doppelstarter_ueber_limite'] = row[i]; i += 1
        yield dict

#-----------
#    from django.db import connection
#    for q in connection.queries:
#        print "--------"
#        print q
#    print "Anzahl Queries", len(connection.queries)
