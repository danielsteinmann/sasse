# -*- coding: utf-8 -*-

import datetime

from django.test import TestCase

from sasse.models import Kategorie
from sasse.models import Mitglied
from sasse.models import Sektion
from sasse.models import Wettkampf
from sasse.models import Schiffeinzel

class KategorieTestCase(TestCase):
    fixtures = ["disziplinarten.json", "kategorien.json"]

    def setUp(self):
        self.jahr = 2009
        testcup = Wettkampf.objects.create(name="Test-Cup",
                zusatz="Bremgarten", von=datetime.date(self.jahr, 5, 14))
        self.einzel = testcup.disziplin_set.create(name="gross")
        self.kat_I = Kategorie.objects.get(name='I')
        self.kat_II = Kategorie.objects.get(name='II')
        self.kat_III = Kategorie.objects.get(name='III')
        self.kat_C = Kategorie.objects.get(name='C')
        self.kat_D = Kategorie.objects.get(name='D')
        self.kat_FII = Kategorie.objects.get(name='FII')
        self.kat_FIII = Kategorie.objects.get(name='FIII')
        self.kat_F = Kategorie.objects.get(name='F')
        self.sektion = Sektion.objects.create(name="Wurstlikon")

    def _assert_kat(self, mitglied):
        s = Schiffeinzel(disziplin=self.einzel, startnummer=1)
        kat = s.calc_kategorie(self.jahr, mitglied)
        alter = self.jahr - mitglied.geburtsdatum.year
        if alter < 15:
            self.assertEqual(self.kat_I, kat)
        elif alter < 18:
            self.assertEqual(self.kat_II, kat)
        elif alter < 21:
            self.assertEqual(self.kat_III, kat)
        elif alter < 43:
            self.assertEqual(self.kat_C, kat)
        else:
            self.assertEqual(self.kat_D, kat)

    def testMannAlleJahre(self):
        for alter in range(1,100):
            jahrgang = self.jahr - alter
            ein_mann = Mitglied.objects.create(
                nummer=alter, name="Hans", vorname="Muster", geschlecht="m",
                geburtsdatum=datetime.date(jahrgang, 1, 1),
                sektion=self.sektion)
            self._assert_kat(ein_mann)

    def testFrauAlleJahre(self):
        for alter in range(1,100):
            jahrgang = self.jahr - alter
            eine_frau = Mitglied.objects.create(
                nummer=alter, name="Nina", vorname="Meier", geschlecht="f",
                geburtsdatum=datetime.date(jahrgang, 1, 1),
                sektion=self.sektion)
            self._assert_kat(eine_frau)


class StartkategorieTestCase(TestCase):
    fixtures = ["disziplinarten.json", "kategorien.json"]

    def setUp(self):
        jahr = 2009
        testcup = Wettkampf.objects.create(name="Test-Cup",
                zusatz="Bremgarten", von=datetime.date(jahr, 5, 14))
        self.einzel = testcup.disziplin_set.create(name="gross")
        self.kat = {}
        for k in Kategorie.objects.all():
            self.kat[k.name] = k
        self.eine_sektion = Sektion.objects.create(name="Wurstlikon")
        def mitglied_mf(alter):
            jahrgang = jahr - alter
            geburi = datetime.date(jahrgang, 1, 1)
            return (
                Mitglied(nummer=alter, name="Luusbueb", vorname="Hans",
                    geschlecht="m", geburtsdatum=geburi,
                    sektion=self.eine_sektion),
                Mitglied(nummer=alter, name="Girlie", vorname="Ida",
                    geschlecht="f", geburtsdatum=geburi,
                    sektion=self.eine_sektion) )
        self.mann_I, self.frau_I = mitglied_mf(14)
        self.mann_II, self.frau_II = mitglied_mf(16)
        self.mann_III, self.frau_III = mitglied_mf(19)
        self.mann_C, self.frau_C = mitglied_mf(30)
        self.mann_D, self.frau_D = mitglied_mf(50)

    def _assert_kat(self, expected, a, b, jpsm=False):
        self.einzel.wettkampf.JPSM = jpsm
        s = Schiffeinzel(disziplin=self.einzel, startnummer=1)
        s.steuermann = a
        s.vorderfahrer = b
        self.assertEqual(expected, s.calc_startkategorie())
        s.steuermann = b
        s.vorderfahrer = a
        self.assertEqual(expected, s.calc_startkategorie())

    def testI(self):
        expected = self.kat['I']
        self._assert_kat(expected, self.mann_I, self.mann_I)
        self._assert_kat(expected, self.mann_I, self.frau_I)
        self._assert_kat(expected, self.frau_I, self.frau_I)
        self._assert_kat(expected, self.frau_I, self.frau_I, jpsm=True)

    def testII(self):
        expected = self.kat['II']
        self._assert_kat(expected, self.mann_II, self.mann_II)
        self._assert_kat(expected, self.mann_II, self.mann_I)
        self._assert_kat(expected, self.mann_II, self.frau_II)
        self._assert_kat(expected, self.mann_II, self.frau_I)

    def testIII(self):
        expected = self.kat['III']
        self._assert_kat(expected, self.mann_III, self.mann_III)
        self._assert_kat(expected, self.mann_III, self.mann_II)
        self._assert_kat(expected, self.mann_III, self.mann_I)
        self._assert_kat(expected, self.mann_III, self.frau_III)
        self._assert_kat(expected, self.mann_III, self.frau_II)
        self._assert_kat(expected, self.mann_III, self.frau_I)

    def testC(self):
        expected = self.kat['C']
        self._assert_kat(expected, self.mann_C, self.mann_C)
        self._assert_kat(expected, self.mann_C, self.mann_D)
        self._assert_kat(expected, self.mann_C, self.mann_II)
        self._assert_kat(expected, self.mann_C, self.mann_III)
        self._assert_kat(expected, self.mann_C, self.frau_C)
        self._assert_kat(expected, self.mann_C, self.frau_D)
        self._assert_kat(expected, self.mann_C, self.frau_II)
        self._assert_kat(expected, self.mann_C, self.frau_III)
        self._assert_kat(expected, self.frau_C, self.mann_C)
        self._assert_kat(expected, self.frau_C, self.mann_D)
        self._assert_kat(expected, self.frau_C, self.mann_II)
        self._assert_kat(expected, self.frau_C, self.mann_III)

    def testD(self):
        expected = self.kat['D']
        self._assert_kat(expected, self.mann_D, self.mann_D)
        self._assert_kat(expected, self.mann_D, self.frau_D)

    def testFII(self):
        expected = self.kat['FII']
        self._assert_kat(expected, self.frau_II, self.frau_II)
        self._assert_kat(expected, self.frau_II, self.frau_I)
        self._assert_kat(expected, self.frau_II, self.frau_II, jpsm=True)
        self._assert_kat(expected, self.frau_II, self.frau_I, jpsm=True)

    def testFIII(self):
        expected = self.kat['FIII']
        self._assert_kat(expected, self.frau_III, self.frau_III)
        self._assert_kat(expected, self.frau_III, self.frau_II)
        self._assert_kat(expected, self.frau_III, self.frau_I)
        self._assert_kat(expected, self.frau_III, self.frau_III, jpsm=True)
        self._assert_kat(expected, self.frau_III, self.frau_II, jpsm=True)
        self._assert_kat(expected, self.frau_III, self.frau_I, jpsm=True)

    def testF(self):
        expected = self.kat['F']
        for f in [self.frau_C, self.frau_D]:
            self._assert_kat(expected, f, self.frau_II)
            self._assert_kat(expected, f, self.frau_III)
            self._assert_kat(expected, f, self.frau_C)
            self._assert_kat(expected, f, self.frau_D)

    def testUnbekannteKombination(self):
        self._assert_kat(None, self.mann_I, self.mann_C)
        self._assert_kat(None, self.frau_III, self.frau_C, jpsm=True)
        self._assert_kat(None, self.mann_C, self.mann_C, jpsm=True)
        self._assert_kat(None, self.mann_D, self.mann_C, jpsm=True)

