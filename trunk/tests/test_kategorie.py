# -*- coding: utf-8 -*-

import datetime
import unittest

from django.test import TestCase

from sasse.forms import get_kategorie
from sasse.forms import get_startkategorie
from sasse.models import Kategorie
from sasse.models import Mitglied
from sasse.models import Sektion


class get_kategorie_Test(TestCase):
    def setUp(self):
        self.jahr = 2009
        self.kat_I = Kategorie.objects.get(name='I')
        self.kat_II = Kategorie.objects.get(name='II')
        self.kat_III = Kategorie.objects.get(name='III')
        self.kat_C = Kategorie.objects.get(name='C')
        self.kat_D = Kategorie.objects.get(name='D')
        self.kat_F = Kategorie.objects.get(name='F')
        bremgarten = Sektion.objects.create(name="Bremgarten")
        self.mann_C = Mitglied.objects.create(
                name="Steinmann", vorname="Daniel", geschlecht="m",
                geburtsdatum=datetime.date(1967, 4, 30),
                sektion=bremgarten)
        self.mann_D = Mitglied.objects.create(
                name="Wendel", vorname="René", geschlecht="m",
                geburtsdatum=datetime.date(1958, 1, 1),
                sektion=bremgarten)
        self.frau_F = Mitglied.objects.create(
                name="Honegger", vorname="Patricia", geschlecht="f",
                geburtsdatum=datetime.date(1977, 1, 1),
                sektion=bremgarten)
        self.frau_II = Mitglied.objects.create(
                name="Leemann", vorname="Sarah", geschlecht="f",
                geburtsdatum=datetime.date(1993, 1, 1),
                sektion=bremgarten)

    def testFrauNichtInKatF(self):
        self.assertEquals(self.kat_II, get_kategorie(self.jahr, self.frau_II))

    def testFrau(self):
        self.assertEquals(self.kat_F, get_kategorie(self.jahr, self.frau_F))

    def testMannKatC(self):
        self.assertEquals(self.kat_C, get_kategorie(self.jahr, self.mann_C))

    def testMannKatD(self):
        self.assertEquals(self.kat_D, get_kategorie(self.jahr, self.mann_D))


class get_startkategorie_Test(unittest.TestCase):
    def setUp(self):
        self.kat_I = Kategorie.objects.get(name='I')
        self.kat_II = Kategorie.objects.get(name='II')
        self.kat_III = Kategorie.objects.get(name='III')
        self.kat_C = Kategorie.objects.get(name='C')
        self.kat_D = Kategorie.objects.get(name='D')
        self.kat_F = Kategorie.objects.get(name='F')

    def _assert_kat(self, expected, a, b):
        self.assertEquals(expected, get_startkategorie(a, b))
        self.assertEquals(expected, get_startkategorie(b, a))

    def testGleicheKategorie(self):
        for k in Kategorie.objects.all():
            self.assertEquals(k, get_startkategorie(k, k))

    def testKatIIandI(self):
        self._assert_kat(self.kat_II, self.kat_I, self.kat_II)

    def testKatIIIandI(self):
        self._assert_kat(self.kat_III, self.kat_I, self.kat_III)

    def testKatIIIandII(self):
        self._assert_kat(self.kat_III, self.kat_II, self.kat_III)

    def testKatCandIII(self):
        self._assert_kat(self.kat_C, self.kat_C, self.kat_III)

    def testKatCandD(self):
        self._assert_kat(self.kat_C, self.kat_C, self.kat_D)

    def testKatCandF(self):
        self._assert_kat(self.kat_C, self.kat_C, self.kat_F)

    def testKatDandF(self):
        self._assert_kat(self.kat_C, self.kat_D, self.kat_F)

    def testUnbekannteKombination(self):
        self._assert_kat(None, self.kat_II, self.kat_C)
        self._assert_kat(None, self.kat_I, self.kat_D)
        self._assert_kat(None, self.kat_I, self.kat_F)
