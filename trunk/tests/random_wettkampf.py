# -*- coding: utf-8 -*-

import sys
import random
from decimal import Decimal
from datetime import date
from sasse.models import Wettkampf
from sasse.models import Disziplin
from sasse.models import Posten
from sasse.models import Postenart
from sasse.models import Sektion
from sasse.models import Mitglied
from sasse.models import Schiffeinzel
from sasse.models import Kategorie
from sasse.models import Bewertung
from sasse.models import Bewertungsart
from sasse.models import Teilnehmer
from sasse.forms import get_startkategorie, get_kategorie

wettkampf_name = "My-Next-Test"
for w in Wettkampf.objects.filter(name=wettkampf_name):
    w.delete()
wettkampf = Wettkampf.objects.create(name=wettkampf_name, zusatz="Bla", von=date.today())
disziplin = Disziplin.objects.create(name="Einzelfahren", wettkampf=wettkampf)
for k in Kategorie.objects.all():
    disziplin.kategorien.add(k)
postenarten = Postenart.objects.filter(disziplinarten__disziplin=disziplin.disziplinart)
for i, postenart in enumerate(postenarten):
    p = Posten.objects.create(name=chr(i+65), disziplin=disziplin, postenart=postenart, reihenfolge=i)

startnummer = 1
for s in Sektion.objects.all():
    mitglieder = list(Mitglied.objects.filter(sektion=s).order_by('geburtsdatum'))
    for i in xrange(0, len(mitglieder), 2):
        hinten = mitglieder[i]
        if len(mitglieder) > i+1:
            vorne = mitglieder[i+1]
        else:
            # Doppelstarter
            vorne = mitglieder[i-1]
        jahr = disziplin.wettkampf.jahr()
        steuermann_kat = get_kategorie(jahr, hinten)
        vorderfahrer_kat = get_kategorie(jahr, vorne)
        kategorie = get_startkategorie(steuermann_kat, vorderfahrer_kat)
        if kategorie:
            schiff = Schiffeinzel.objects.create(disziplin=disziplin, startnummer=startnummer,
                    steuermann=hinten, vorderfahrer=vorne, sektion=s,
                    kategorie=kategorie)
            startnummer += 1
    print u"Startliste für %s erzeugt" % s
schiffe = Teilnehmer.objects.filter(disziplin=disziplin)
for p in disziplin.posten_set.all():
    for bart in Bewertungsart.objects.filter(postenart=p.postenart, editierbar=True):
        gueltige_werte_str = bart.wertebereich
        gueltige_werte = [Decimal(v.strip()) for v in gueltige_werte_str.split(',')]
        for s in schiffe:
            b = Bewertung(teilnehmer=s, posten=p, bewertungsart=bart)
            if p.postenart.name == 'Zeitnote':
                b.zeit = Decimal(random.randrange(20, 40, 1))
            else:
                b.note = Decimal(random.choice(gueltige_werte))
            b.save()
    print u"Werte für Posten %s erzeugt" % p



def main(argv=None):
    if argv is None:
        argv = sys.argv
    return 0

if __name__ == "__main__":
    sys.exit(main())

