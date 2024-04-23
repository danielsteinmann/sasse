# -*- coding: utf-8 -*-

from decimal import Decimal
import datetime

from django.test import TestCase

from sasse.models import *
from sasse.queries import read_doppelstarter


class DoppelstarterEinzelTest(TestCase):
    def setUp(self):
        self.bremgarten = Sektion.objects.get(name="Bremgarten")
        self.steinmann = Mitglied.objects.create(
                name="Steinmann", vorname="Daniel", geschlecht="m",
                geburtsdatum=datetime.date(1967, 4, 30),
                sektion=self.bremgarten, nummer="1234")
        self.wendel = Mitglied.objects.create(
                name="Wendel", vorname="René", geschlecht="m",
                geburtsdatum=datetime.date(1956, 4, 30),
                sektion=self.bremgarten, nummer="1239")
        self.kohler = Mitglied.objects.create(
                name="Kohler", vorname="Bernhard", geschlecht="m",
                geburtsdatum=datetime.date(1978, 1, 1),
                sektion=self.bremgarten, nummer="1251")
        self.muster = Mitglied.objects.create(
                name="Muster", vorname="Felix", geschlecht="m",
                geburtsdatum=datetime.date(1969, 1, 1),
                sektion=self.bremgarten, nummer="9234")
        self.degen = Mitglied.objects.create(
                name="Degen", vorname="Juri", geschlecht="m",
                geburtsdatum=datetime.date(2000, 4, 30),
                sektion=self.bremgarten, nummer="6232")
        self.greber = Mitglied.objects.create(
                name="Greber", vorname="Andreas", geschlecht="m",
                geburtsdatum=datetime.date(2000, 4, 30),
                sektion=self.bremgarten, nummer="6235")
        self.einzelfahren = Disziplinart.objects.get(name="Einzelfahren")
        self.wettkampf = Wettkampf.objects.create(name="Test-Cup", von=datetime.date(2011, 5, 14))
        self.einzel_gross = self.wettkampf.disziplin_set.create(name="Einzel-Gross")
        self.einzel_klein = self.wettkampf.disziplin_set.create(name="Einzel-Klein")
        self.kat_C = Kategorie.objects.get(name="C")
        self.kat_D = Kategorie.objects.get(name="D")
        self.kat_I = Kategorie.objects.get(name="I")
        # Normaler Starter
        stnr1 = Schiffeinzel.objects.create(startnummer=1,
                steuermann=self.steinmann, vorderfahrer=self.wendel,
                sektion=self.bremgarten, kategorie=self.kat_D,
                disziplin=self.einzel_gross)

    def testRegulaererDoppelstarter(self):
        dsHinten = Schiffeinzel.objects.create(startnummer=2,
                steuermann=self.steinmann, steuermann_ist_ds=True,
                vorderfahrer=self.kohler,
                sektion=self.bremgarten, kategorie=self.kat_D,
                disziplin=self.einzel_gross)
        dsVorne = Schiffeinzel.objects.create(startnummer=3,
                steuermann=self.muster,
                vorderfahrer=self.wendel, vorderfahrer_ist_ds=True,
                sektion=self.bremgarten, kategorie=self.kat_D,
                disziplin=self.einzel_gross)
        ds = read_doppelstarter(self.wettkampf, self.einzelfahren)
        self.assertEqual(2, len(ds))
        self.assertEqual(1, len(ds[0]['doppel']))
        self.assertEqual(1, len(ds[0]['normal']))
        self.assertEqual(1, len(ds[1]['doppel']))
        self.assertEqual(1, len(ds[1]['normal']))

    def testSortiertNachDoppelstarternummer(self):
        dsHinten = Schiffeinzel.objects.create(startnummer=153,
                steuermann=self.steinmann, steuermann_ist_ds=True,
                vorderfahrer=self.kohler,
                sektion=self.bremgarten, kategorie=self.kat_D,
                disziplin=self.einzel_gross)
        dsVorne = Schiffeinzel.objects.create(startnummer=151,
                steuermann=self.muster,
                vorderfahrer=self.wendel, vorderfahrer_ist_ds=True,
                sektion=self.bremgarten, kategorie=self.kat_D,
                disziplin=self.einzel_gross)
        ds = read_doppelstarter(self.wettkampf, self.einzelfahren)
        self.assertEqual(2, len(ds))
        self.assertEqual(151, ds[0]['doppel'][0]['startnummer'])
        self.assertEqual(153, ds[1]['doppel'][0]['startnummer'])

    def testNichtMarkierteDoppelstarter(self):
        dsHinten = Schiffeinzel.objects.create(startnummer=2,
                steuermann=self.steinmann, steuermann_ist_ds=False,
                vorderfahrer=self.kohler,
                sektion=self.bremgarten, kategorie=self.kat_D,
                disziplin=self.einzel_gross)
        dsVorne = Schiffeinzel.objects.create(startnummer=3,
                steuermann=self.muster,
                vorderfahrer=self.wendel, vorderfahrer_ist_ds=False,
                sektion=self.bremgarten, kategorie=self.kat_D,
                disziplin=self.einzel_gross)
        ds = read_doppelstarter(self.wettkampf, self.einzelfahren)
        self.assertEqual(2, len(ds))
        self.assertEqual(0, len(ds[0]['doppel']))
        self.assertEqual(2, len(ds[0]['normal']))
        self.assertEqual(0, len(ds[1]['doppel']))
        self.assertEqual(2, len(ds[1]['normal']))

    def testMarkiertAberNichtDoppelstarter(self):
        dsHinten = Schiffeinzel.objects.create(startnummer=2,
                steuermann=self.muster, steuermann_ist_ds=True,
                vorderfahrer=self.kohler,
                sektion=self.bremgarten, kategorie=self.kat_D,
                disziplin=self.einzel_gross)
        dsVorne = Schiffeinzel.objects.create(startnummer=3,
                steuermann=self.degen,
                vorderfahrer=self.greber, vorderfahrer_ist_ds=True,
                sektion=self.bremgarten, kategorie=self.kat_I,
                disziplin=self.einzel_klein)
        ds = read_doppelstarter(self.wettkampf, self.einzelfahren)
        self.assertEqual(2, len(ds))
        self.assertEqual(1, len(ds[0]['doppel']))
        self.assertEqual(0, len(ds[0]['normal']))
        self.assertEqual(1, len(ds[1]['doppel']))
        self.assertEqual(0, len(ds[1]['normal']))
