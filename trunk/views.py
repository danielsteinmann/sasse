from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.forms import ModelForm, ValidationError
from django import forms
from django.shortcuts import get_object_or_404, get_list_or_404
from django.shortcuts import render_to_response
from django.template.defaultfilters import slugify
from models import Wettkampf
from models import Disziplin
from models import Kategorie
from django.shortcuts import render_to_response


def wettkaempfe_get(request):
    assert request.method == 'GET'
    liste = Wettkampf.objects.all().order_by('-von')
    return render_to_response('wettkampf_list.html', {'liste': liste})

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
        slug = form.cleaned_data['slug']
        return HttpResponseRedirect(reverse(wettkampf_get, args=[slug]))
    return render_to_response('wettkampf_add.html', {'form': form,})

def wettkaempfe_by_year(request, jahr):
    assert request.method == 'GET'
    liste = Wettkampf.objects.all().order_by('-von')
    return render_to_response('wettkampf_list.html', {'liste': liste})

def wettkampf_get(request, wettkampf):
    assert request.method == 'GET'
    w = get_object_or_404(Wettkampf, slug=wettkampf)
    d = w.disziplin_set.all()
    return render_to_response('wettkampf.html',
            {'wettkampf': w, 'disziplinen': d})

def wettkampf_update(request, wettkampf):
    if request.method == 'POST':
        return wettkampf_put(request, wettkampf)
    assert request.method == 'GET'
    w = get_object_or_404(Wettkampf, slug=wettkampf)
    d = w.disziplin_set.all()
    form = WettkampfForm(instance=w)
    return render_to_response('wettkampf_update.html',
            {'wettkampf': w, 'disziplinen': d, 'form': form})

def wettkampf_put(request, wettkampf):
    assert request.method == 'POST'
    w = get_object_or_404(Wettkampf, slug=wettkampf)
    form = WettkampfForm(request.POST, instance=w)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(wettkampf_get, args=[wettkampf]))
    return render_to_response('wettkampf_update.html',
            {'form': form,})

def wettkampf_delete_confirm(request, wettkampf):
    if request.method == 'POST':
        return wettkampf_delete(request, wettkampf)
    assert request.method == 'GET'
    w = get_object_or_404(Wettkampf, slug=wettkampf)
    return render_to_response('wettkampf_delete.html', {'wettkampf': w})

def wettkampf_delete(request, wettkampf):
    assert request.method == 'POST'
    w = get_object_or_404(Wettkampf, slug=wettkampf)
    w.delete()
    return HttpResponseRedirect(reverse(wettkaempfe_get))

def disziplinen_add(request, wettkampf):
    if request.method == 'POST':
        return disziplinen_post(request, wettkampf)
    assert request.method == 'GET'
    w = get_object_or_404(Wettkampf, slug=wettkampf)
    form = DisziplinForm()
    return render_to_response('disziplin_add.html',
            {'form': form, 'wettkampf': w})

def disziplinen_post(request, wettkampf):
    assert request.method == 'POST'
    w = get_object_or_404(Wettkampf, slug=wettkampf)
    form = DisziplinForm(request.POST)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.name = instance.disziplinart.name
        if instance.disziplinart.pk == 1: # Einzelfahren
            for k in form.cleaned_data['kategorien']:
                instance.name += '_%s' % (k.name,)
        # Weil das 'wettkampf' Feld nicht editierbar ist
        instance.wettkampf = w
        instance.save()
        form.save_m2m()
        return HttpResponseRedirect(reverse(wettkampf_get, args=[wettkampf]))
    return render_to_response('disziplin_add.html',
            {'form': form, 'wettkampf': w})

def disziplin_get(request, wettkampf, disziplin):
    assert request.method == 'GET'
    w = get_object_or_404(Wettkampf, slug=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    form = DisziplinForm()
    return render_to_response('disziplin.html',
            {'form': form, 'wettkampf': w})

def disziplin_update(request, wettkampf, disziplin):
    if request.method == 'POST':
        return disziplin_put(request, wettkampf, disziplin)
    assert request.method == 'GET'
    w = get_object_or_404(Wettkampf, slug=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    form = DisziplinForm(instance=d)
    return render_to_response('disziplin_add.html',
            {'form': form, 'wettkampf': w})

def disziplin_put(request, wettkampf, disziplin):
    assert request.method == 'POST'
    w = get_object_or_404(Wettkampf, slug=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    form = DisziplinForm(request.POST, instance=d)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(wettkampf_update, args=[wettkampf]))
    return render_to_response('disziplin_add.html',
            {'form': form, 'wettkampf': w})

class WettkampfForm(ModelForm):

    class Meta:
        model = Wettkampf

    def clean(self):
        cleaned_data = self.cleaned_data
        von = cleaned_data.get("von")
        bis = cleaned_data.get("bis")

        if von and bis:
            if bis < von:
                raise ValidationError("Von muss aelter als bis sein")

        return cleaned_data


class DisziplinForm(ModelForm):

    kategorien = forms.ModelMultipleChoiceField(
            queryset=Kategorie.objects.all(),
            widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Disziplin
        exclude = ('name',)
