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
from sasse.models import Richtzeit

def delete_wettkampf(wettkampf_name):
    for w in Wettkampf.objects.filter(name=wettkampf_name):
        w.delete()
    print("Alte Daten für Wettkampf %s gelöscht" % wettkampf_name)

def create_einzelfahren(wettkampf_name):
    wettkampf = Wettkampf.objects.create(
            name=wettkampf_name,
            zusatz="Bla",
            von=date.today())
    disziplin = Disziplin.objects.create(
            name="Einzelfahren",
            wettkampf=wettkampf)
    for k in Kategorie.objects.all():
        disziplin.kategorien.add(k)
    return disziplin

def create_parcour(disziplin):
    anzahl_normale_posten = 12
    postenarten = Postenart.objects.filter(
            disziplinarten__disziplin=disziplin.disziplinart).exclude(name="Zeitnote")
    for i in range(0, anzahl_normale_posten):
        postenart = random.choice(postenarten)
        name = chr(i+64)
        p = Posten.objects.create(
                name=chr(i+65),
                disziplin=disziplin,
                postenart=postenart,
                reihenfolge=i)

    anzahl_zeit_posten = 3
    zeitnote = Postenart.objects.get(
            disziplinarten__disziplin=disziplin.disziplinart,
            name="Zeitnote")
    for i in range(0, anzahl_zeit_posten):
        p = Posten.objects.create(
                name="A-"+chr(i+65),
                disziplin=disziplin,
                postenart=zeitnote,
                reihenfolge=anzahl_normale_posten+1+i)
        random_zeit = Decimal(str(random.uniform(40.0, 150.0)))
        richtzeit = Richtzeit.objects.create(posten=p, zeit=random_zeit)

def create_startliste(disziplin):
    sys.stdout.write("Erzeuge Startlisten für ")
    startnummer = 1
    for s in Sektion.objects.all():
        sys.stdout.write("%s " % s)
        sys.stdout.flush()
        mitglieder = list(Mitglied.objects.filter(sektion=s).order_by('geburtsdatum'))
        for i in range(0, len(mitglieder), 2):
            hinten = mitglieder[i]
            if len(mitglieder) > i+1:
                vorne = mitglieder[i+1]
            else:
                # Doppelstarter
                vorne = mitglieder[i-1]
            schiff = Schiffeinzel(
                    disziplin=disziplin,
                    startnummer=startnummer,
                    steuermann=hinten,
                    vorderfahrer=vorne,
                    sektion=s)
            kategorie = schiff.calc_startkategorie()
            if kategorie:
                schiff.kategorie = kategorie
                schiff.save()
                startnummer += 1
    sys.stdout.write("\n")

def create_noten(disziplin):
    sys.stdout.write("Erzeuge Noten für Posten ")
    schiffe = list(Teilnehmer.objects.filter(disziplin=disziplin))
    for p in disziplin.posten_set.all():
        sys.stdout.write("%s " % p)
        sys.stdout.flush()
        richtzeit = None
        if p.postenart.name == 'Zeitnote':
            richtzeit = float(Richtzeit.objects.get(posten=p).zeit)
            zeit_from = richtzeit - (richtzeit * 0.05)
            zeit_until = richtzeit * 2
        for bart in Bewertungsart.objects.filter(postenart=p.postenart, editierbar=True):
            gueltige_werte_str = bart.wertebereich
            gueltige_werte = [Decimal(v.strip()) for v in gueltige_werte_str.split(',')]
            for s in schiffe:
                b = Bewertung(teilnehmer=s, posten=p, bewertungsart=bart)
                if richtzeit:
                    b.zeit = Decimal(str(random.uniform(zeit_from, zeit_until)))
                    b.save()
                else:
                    random_note = Decimal(random.choice(gueltige_werte))
                    if random_note != bart.defaultwert:
                        b.note = Decimal(random_note)
                        b.save()
    sys.stdout.write("\n")

def main(argv=None):
    if argv is None:
        argv = sys.argv
    wettkampf_name = "Load-Test"
    if len(argv) > 1:
        wettkampf_name = argv[1]
    delete_wettkampf(wettkampf_name)
    einzelfahren = create_einzelfahren(wettkampf_name)
    create_parcour(einzelfahren)
    create_startliste(einzelfahren)
    create_noten(einzelfahren)
    return 0

if __name__ == "__main__":
    sys.exit(main())

