from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.forms import ModelForm, ValidationError
from django import forms
from django.shortcuts import get_object_or_404, get_list_or_404
from django.shortcuts import render_to_response
from models import Wettkampf
from models import Disziplin
from models import Kategorie
from django.shortcuts import render_to_response


def wettkaempfe_get(request):
    assert request.method == 'GET'
    liste = Wettkampf.objects.all()
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
        jahr = form.cleaned_data['von'].year
        name = form.cleaned_data['name']
        return HttpResponseRedirect(reverse(wettkampf_get, args=[jahr, name]))
    return render_to_response('wettkampf_add.html', {'form': form,})

def wettkaempfe_by_year(request, jahr):
    assert request.method == 'GET'
    liste = Wettkampf.objects.filter(von__year=jahr)
    return render_to_response('wettkampf_list.html',
            {'liste': liste, 'year': jahr})

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
        return HttpResponseRedirect(reverse(wettkampf_update, args=[jahr, wettkampf]))
    return render_to_response('disziplin_add.html',
            {'form': form, 'wettkampf': w})

def disziplin_get(request, jahr, wettkampf, disziplin):
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    form = DisziplinForm()
    return render_to_response('disziplin.html',
            {'form': form, 'wettkampf': w})

def disziplin_update(request, jahr, wettkampf, disziplin):
    if request.method == 'POST':
        return disziplin_put(request, jahr, wettkampf, disziplin)
    assert request.method == 'GET'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    form = DisziplinForm(instance=d)
    return render_to_response('disziplin_add.html',
            {'form': form, 'wettkampf': w})

def disziplin_put(request, jahr, wettkampf, disziplin):
    assert request.method == 'POST'
    w = Wettkampf.objects.get(von__year=jahr, name=wettkampf)
    d = Disziplin.objects.get(wettkampf=w, name=disziplin)
    form = DisziplinForm(request.POST.copy(), instance=d)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse(wettkampf_update, args=[jahr, wettkampf]))
    return render_to_response('disziplin_add.html',
            {'form': form, 'wettkampf': w})


class WettkampfForm(ModelForm):

    class Meta:
        model = Wettkampf


    def clean(self):
        cleaned_data = self.cleaned_data
        von = cleaned_data.get("von")
        bis = cleaned_data.get("bis")
        name = cleaned_data.get("name")

        if von and bis:
            if bis < von:
                raise ValidationError("Von muss aelter als bis sein")

        if von and name:
            q = Wettkampf.objects.filter(name=name, von__year=von.year)
            # Remove current Wettkampf from queryset
            q = q.exclude(id=self.instance.id)
            if q.count() > 0:
                raise ValidationError("Der Name '%s' ist im Jahr '%d' "
                        "bereits vergeben" % (name, von.year))

        return cleaned_data


class DisziplinForm(ModelForm):
    wettkampf = forms.ModelChoiceField(
            queryset=Wettkampf.objects.all(),
            widget=forms.HiddenInput)
    name = forms.CharField(initial='(Wird automatisch gefuellt)')

    class Meta:
        model = Disziplin

    def clean(self):
        cleaned_data = self.cleaned_data
        if self.instance.id is None:
            cleaned_data['name'] = self._default_name()
        q = Disziplin.objects.filter(
                wettkampf=cleaned_data['wettkampf'],
                disziplinart=cleaned_data['disziplinart'],
                name=cleaned_data['name'])
        # Remove current object from queryset
        q = q.exclude(id=self.instance.id)
        if q.count() > 0:
            # Make sure newly created name is displayed
            self.data['name'] = cleaned_data['name']
            raise ValidationError(
                    "Name '%s' fuer Disziplinart '%s' bereits vergeben"
                    % (cleaned_data['name'], cleaned_data['disziplinart']))
        return cleaned_data

    def _default_name(self):
        disziplinart = self.cleaned_data['disziplinart']
        default_name = disziplinart.name
        if disziplinart.pk == 1: # Einzelfahren
            for k in self.cleaned_data['kategorien']:
                default_name += '_%s' % (k.name,)
        return default_name

