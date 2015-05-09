# -*- coding: utf-8 -*-

import csv
import operator
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from sasse.models import Teilnehmer
from sasse.models import Bewertung
from sasse.models import Bewertungsart
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
