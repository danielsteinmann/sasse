# -*- coding: utf-8 -*-

import csv
import operator
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from sasse.models import Teilnehmer
from sasse.models import Bewertung
from sasse.models import Bewertungsart
from sasse.models import Schiffsektion
from sasse.forms import BewertungForm

def load_einzelfahren(wettkampf, disziplin, posten, csvfile):
    #fieldnames = ['Platz', 'Nr.', 'Name und Vorname', 'Kategorie', 'Ziel Zeit', 'Abstand']
    zeiten = csv.reader(csvfile, delimiter='\t')
    bewertungsart = Bewertungsart.objects.get(postenart=posten.postenart)
    success = 0
    failed = {}
    for row in zeiten:
        if len(row) < 2 or not row[1].strip().isdigit():
            continue
        startnr = int(row[1])
        try:
            teilnehmer = Teilnehmer.objects.get(disziplin=disziplin,
                    startnummer=startnr)
        except Teilnehmer.DoesNotExist:
            failed[startnr] = u"Startnummer nicht gefunden"
            continue
        zeit_str = row[4].strip()
        kwargs = {'posten': posten, 'bewertungsart': bewertungsart,
                'teilnehmer_id': teilnehmer.id}
        form = BewertungForm(data={'wert': zeit_str}, **kwargs)
        if not form.is_valid():
            failed[startnr] = u"Ungültiges Zeitformat: {0}".format(zeit_str)
            continue
        zeit = form.cleaned_data['wert']
        b, created = Bewertung.objects.get_or_create(defaults={'zeit': zeit},
                **kwargs)
        if created:
            success += 1
        else:
            failed[startnr] = u"Bereits eine Zeit vorhanden: {0}".format(b)
    failed_sorted = sorted(failed.items(), key=operator.itemgetter(0))
    return (success, failed_sorted)

def load_sektionsfahren(p1, p2, formset, csvfile):
    #fieldnames = ['Platz', 'Nr.', 'Name und Vorname', 'Kategorie', 'Ziel Zeit', 'Abstand']
    zeiten = csv.reader(csvfile, delimiter='\t')
    zeit_by_startnr = {}
    for row in zeiten:
        if len(row) < 2 or not row[1].strip().isdigit():
            continue
        startnr = int(row[1])
        zeit_str = row[4].strip()
        zeit_by_startnr[startnr] = zeit_str

    bewertungsart = Bewertungsart.objects.get(name='Zeit')
    success = set()
    failed = {}
    for form in formset.forms:
        row = form.cleaned_data
        gruppe_id = row['gruppe_id']
        for s in Schiffsektion.objects.filter(gruppe=row['gruppe_id']):
            for posten in (p1, p2):
                kwargs = {'posten': posten, 'bewertungsart': bewertungsart,
                        'teilnehmer_id': s.teilnehmer_ptr_id}
                erste_startnr = row['erste_startnr_durchgang_' + posten.name[-1]]
                if erste_startnr is None:
                    continue
                startnr = int(erste_startnr) + (s.position - 1)
                zeit_str = zeit_by_startnr.get(startnr)
                if zeit_str is None:
                    failed[startnr] = u"Keine Zeit im File gefunden"
                    continue
                form = BewertungForm(data={'wert': zeit_str}, **kwargs)
                if not form.is_valid():
                    failed[startnr] = u"Ungültiges Zeitformat: {0}".format(zeit_str)
                    continue
                zeit = form.cleaned_data['wert']
                b, created = Bewertung.objects.get_or_create(defaults={'zeit': zeit},
                        **kwargs)
                if created:
                    success.add(startnr)
                else:
                    failed[startnr] = u"Bereits eine Zeit vorhanden: {0}".format(b)

    unused = set(zeit_by_startnr.keys()) - set(failed.keys()) - success
    for startnr in unused:
        failed[startnr] = u"Zeit keinem Schiff zugeteilt"

    failed_sorted = sorted(failed.items(), key=operator.itemgetter(0))
    return (len(success), failed_sorted)
