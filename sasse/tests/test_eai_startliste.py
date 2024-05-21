# -*- coding: utf-8 -*-

import csv
import datetime
import io

from django.test import TestCase
from django.core.cache import cache

from sasse import eai_startliste
from sasse.models import *
from sasse.eai_startliste import StartlisteImportException
from sasse.eai_startliste import load as load_startliste
from sasse.eai_startliste import dump as dump_startliste
from sasse.eai_startliste import cru_mitglied
from sasse.eai_startliste import serialize_schiffeinzel


class MitgliedImportTest(TestCase):
    fixtures = ["disziplinarten.json", "kategorien.json"]

    def setUp(self):
        self.bremgarten = Sektion.objects.create(name="Bremgarten")
        self.steinmann = Mitglied.objects.create(
                nummer="10043",
                name="Steinmann",
                vorname="Daniel",
                geschlecht="m",
                geburtsdatum=datetime.date(1967, 4, 30),
                sektion=self.bremgarten)

    def testMitgliedGefunden(self):
        row = {
                "STEUERMANN_NUMMER": self.steinmann.nummer,
                "STEUERMANN_NAME": self.steinmann.name,
                "STEUERMANN_VORNAME": self.steinmann.vorname,
                "STEUERMANN_GEBURTSDATUM": str(self.steinmann.geburtsdatum),
                "STEUERMANN_GESCHLECHT": self.steinmann.geschlecht,
                "STEUERMANN_SEKTION_NAME": self.steinmann.sektion.name.encode('utf-8'),
                }
        mitglied = cru_mitglied("STEUERMANN", row)
        self.assertEqual(self.steinmann, mitglied)

    def testMitgliedGeaendert(self):
        anderer_name = "Gugugs"
        row = {
                "STEUERMANN_NUMMER": self.steinmann.nummer,
                "STEUERMANN_NAME": anderer_name,
                "STEUERMANN_VORNAME": self.steinmann.vorname,
                "STEUERMANN_GEBURTSDATUM": str(self.steinmann.geburtsdatum),
                "STEUERMANN_GESCHLECHT": self.steinmann.geschlecht,
                "STEUERMANN_SEKTION_NAME": self.steinmann.sektion.name.encode('utf-8'),
                }
        mitglied = cru_mitglied("STEUERMANN", row)
        self.assertEqual(mitglied.id, self.steinmann.id)
        from_db = Mitglied.objects.get(pk=mitglied.id)
        self.assertEqual(anderer_name, from_db.name)

    def testMitgliedErzeugt(self):
        row = {
                "STEUERMANN_NUMMER": "232",
                "STEUERMANN_NAME": "Muster",
                "STEUERMANN_VORNAME": "Felix",
                "STEUERMANN_GEBURTSDATUM": "2000-01-01",
                "STEUERMANN_GESCHLECHT": "m",
                "STEUERMANN_SEKTION_NAME": "Bremgarten",
                }
        mitglied = cru_mitglied("STEUERMANN", row)
        from_db = Mitglied.objects.get(pk=mitglied.id)
        self.assertEqual("Muster", from_db.name)


class SchiffeinzelImportTest(TestCase):
    fixtures = ["disziplinarten.json", "kategorien.json"]

    def setUp(self):
        cache.clear()
        self.kat_D = Kategorie.objects.get(name="D")
        self.bremgarten = Sektion.objects.create(name="Bremgarten")
        self.testcup = Wettkampf.objects.create(
                name="Fallbaumcup",
                zusatz="Bremgarten",
                von=datetime.date(2011, 5, 14))
        self.einzel_gross = self.testcup.disziplin_set.create(name="Einzelfahren-Gross")
        einzel_klein = self.testcup.disziplin_set.create(name="Einzelfahren-Klein")
        self.steinmann = Mitglied.objects.create(
                nummer="10043",
                name="Steinmann",
                vorname="Daniel",
                geschlecht="m",
                geburtsdatum=datetime.date(1967, 4, 30),
                sektion=self.bremgarten,
                )
        self.wendel = Mitglied.objects.create(
                nummer="10049",
                name="Wendel",
                vorname="René",
                geschlecht="m",
                geburtsdatum=datetime.date(1956, 4, 30),
                sektion=self.bremgarten,
                )
        self.stnr1 = Schiffeinzel.objects.create(
                disziplin=self.einzel_gross,
                startnummer=1,
                steuermann=self.steinmann,
                vorderfahrer=self.wendel,
                sektion=self.bremgarten,
                kategorie=self.kat_D,
                )
        self.csvfile = io.StringIO()
        self.csvwriter = csv.DictWriter(self.csvfile, eai_startliste.COLUMNS)
        self.csvwriter.writeheader()
        self.stnr1 = Schiffeinzel.objects.select_related().get(pk=self.stnr1.id)
        self.row = serialize_schiffeinzel(self.stnr1)

    def testDump(self):
        csvfile = io.StringIO()
        dump_startliste(self.testcup, csvfile)
        self.assertTrue(len(csvfile.getvalue()) > 0)

    def testUnveraendert(self):
        self.csvwriter.writerow(self.row)
        self.csvfile.seek(0)
        stats = load_startliste(self.testcup, self.csvfile)
        self.assertEqual(stats["unchanged"], 1)

    def testGeandert(self):
        self.row['KATEGORIE_NAME'] = "C"
        self.csvwriter.writerow(self.row)
        self.csvfile.seek(0)
        stats = load_startliste(self.testcup, self.csvfile)
        self.assertEqual(stats["update"], 1)

    def testEingefuegt(self):
        self.row['STARTNUMMER'] = 2
        self.csvwriter.writerow(self.row)
        self.csvfile.seek(0)
        stats = load_startliste(self.testcup, self.csvfile)
        self.assertEqual(stats["insert"], 1)

    def testWettkampfExistiertNicht(self):
        self.row['WETTKAMPF_NAME'] = "BlaBla"
        self.csvwriter.writerow(self.row)
        self.csvfile.seek(0)
        with self.assertRaisesRegex(StartlisteImportException, 'Eingelesene Startliste.*'):
            load_startliste(self.testcup, self.csvfile)

    def testDisziplinExistiertNicht(self):
        self.row["DISZIPLIN_NAME"] = "BlaBla"
        self.csvwriter.writerow(self.row)
        self.csvfile.seek(0)
        with self.assertRaisesRegex(StartlisteImportException, 'BlaBla: Wettkampf/Disziplin nicht'):
            load_startliste(self.testcup, self.csvfile)

    def testSektionExistiertNicht(self):
        self.row["SEKTION_NAME"] = "BlaBla"
        self.csvwriter.writerow(self.row)
        self.csvfile.seek(0)
        with self.assertRaisesRegex(StartlisteImportException, 'BlaBla: Keine solche Sektion'):
            load_startliste(self.testcup, self.csvfile)

    def testKategorieExistiertNicht(self):
        self.row["KATEGORIE_NAME"] = "Z"
        self.csvwriter.writerow(self.row)
        self.csvfile.seek(0)
        with self.assertRaisesRegex(StartlisteImportException, 'Z: Keine solche Kategorie'):
            load_startliste(self.testcup, self.csvfile)

    def testFalscheKolonnen(self):
        csvfile = io.StringIO("""\
WETTKAMPF_JAHR,HANSWURST
2011,Fällbaumcup,Einzelfahren-Gross
""".encode("utf-8"))
        with self.assertRaises(KeyError):
            load_startliste(self.testcup, csvfile)
