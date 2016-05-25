# -*- coding: utf-8 -*-

import csv
import operator
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from sasse.models import Teilnehmer
from sasse.models import Bewertung
from sasse.models import Bewertungsart
from sasse.forms import BewertungForm

def load_pfeiler(wettkampf, disziplin, posten, csvfile):
    # BootNr,Ziel,Lappen,Abzugstellung,Abzuganprallen
    # 0001,9.5,false,2,1
    # 0002,10.0,true,0,0
    noten = csv.reader(csvfile, delimiter=',')
    ziel_art = Bewertungsart.objects.get(postenart=posten.postenart,
            gruppe='ZIEL', editierbar=True)
    stil_art = Bewertungsart.objects.get(postenart=posten.postenart,
            gruppe='STIL', editierbar=True)
    success = 0
    failed = {}
    for row in noten:
        if not row[0].strip().isdigit():
            continue
        startnr = int(row[0])
        try:
            teilnehmer = Teilnehmer.objects.get(disziplin=disziplin,
                    startnummer=startnr)
        except Teilnehmer.DoesNotExist:
            failed[startnr] = u"Startnummer nicht gefunden"
            continue
        ziel_note = row[1].strip()
        stil_note = int(row[3].strip()) + int(row[4].strip())
        failures = []
        for note, art in ((ziel_note, ziel_art), (stil_note, stil_art)):
            kwargs = {'posten': posten, 'bewertungsart': art,
                    'teilnehmer_id': teilnehmer.id}
            form = BewertungForm(data={'wert': note}, **kwargs)
            if not form.is_valid():
                failures.append(u"{0}: Ungültiger Wert: {1}".format(art.name, note))
                continue
            note = form.cleaned_data['wert']
            b, created = Bewertung.objects.get_or_create(defaults={'note': note},
                    **kwargs)
            if not created:
                failures.append(u"{0} existiert schon ({1})".format(art.name, b))
        if failures:
            failed[startnr] = "; ".join(failures)
        else:
            success += 1
    failed_sorted = sorted(failed.items(), key=operator.itemgetter(0))
    return (success, failed_sorted)

