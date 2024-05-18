# -*- coding: utf-8 -*-

import os
import json
from datetime import date
from django.core.management.base import BaseCommand, CommandError
from sasse.models import Mitglied, Sektion

class Command(BaseCommand):
    help = 'Importiert SWV Mitglieder Daten aus dem Json File.'

    def add_arguments(self, parser):
        parser.add_argument("JSON-FILE", type=str)

    def handle(self, *args, **options):
        if 'JSON-FILE' not in options:
            raise CommandError('Ein Excel File mit Mitgliederdaten als Input erwartet.')
        path = options['JSON-FILE']
        if not os.path.isfile(path):
            raise CommandError('%s: Ist kein File.' % path)
        with open(path, 'r') as f:
            data = json.load(f)
            club_cache = self.import_sektionen(data['clubs'])
            self.import_mitglieder(data['participants'], club_cache)
        return 0

    def import_sektionen(self, clubs):
        cache = {}
        for i, club in enumerate(clubs):
            verein_name = club['name']
            verein_id = club['FK_VereinID']
            if verein_id:
                try:
                    s = Sektion.objects.get(nummer=verein_id)
                    s.name = verein_name
                    s.save()
                except Sektion.DoesNotExist:
                    s = Sektion()
                    s.nummer = verein_id
                    s.name = verein_name
                    s.save()
                    self.stdout.write(self.style.SUCCESS("Inserted: %s" % s))
                cache[club['id']] = s
        self.stdout.write(self.style.SUCCESS("Import Vereine: %d" % i))
        return cache

    def map_geschlecht(self, swvValue):
        if swvValue == 1:
            return 'f'
        else:
            return 'm'

    def import_mitglieder(self, participants, club_cache):
        for i, participant in enumerate(participants):
            fahrer_id = participant['FK_fahrerID']
            if fahrer_id:
                nummer = "SWV-%d" % fahrer_id
                name = participant['last_name']
                vorname = participant['first_name']
                geburtsdatum = date(participant['year_of_birth'], 1, 1)
                geschlecht = self.map_geschlecht(participant['gender'])
                sektion = club_cache[participant['club_id']]
                try:
                    m = Mitglied.objects.get(nummer=nummer)
                    m.name = name
                    m.vorname = vorname
                    m.geburtsdatum = geburtsdatum
                    m.geschlecht = geschlecht
                    m.sektion = sektion
                    m.save()
                except Mitglied.DoesNotExist:
                    found = False
                    for mitglied in Mitglied.objects.filter(
                            sektion=sektion,
                            name=name,
                            vorname=vorname,
                            geburtsdatum__year=geburtsdatum.year,
                            geschlecht=geschlecht
                            ):
                        found = True
                        msg = "Update Nummer von %s auf %s für %s" % (mitglied.nummer, nummer, mitglied)
                        self.stdout.write(self.style.SUCCESS(msg))
                        mitglied.nummer = nummer
                        mitglied.save()
                    if not found:
                        m = Mitglied()
                        m.nummer = nummer
                        m.name = name
                        m.vorname = vorname
                        m.geburtsdatum = geburtsdatum
                        m.geschlecht = geschlecht
                        m.sektion = sektion
                        m.save()
                        self.stdout.write(self.style.SUCCESS("Inserted: %s" % m))
        self.stdout.write(self.style.SUCCESS("Import Mitglieder: %d" % i))

