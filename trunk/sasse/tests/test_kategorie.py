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
        self.sektion = Sektion.objects.create(name="Wurstlikon")

    def testMannAlleJahre(self):
        for alter in range(1,100):
            jahrgang = self.jahr - alter
            ein_mann = Mitglied.objects.create(
                nummer=alter, name="Hans", vorname="Muster", geschlecht="m",
                geburtsdatum=datetime.date(jahrgang, 1, 1),
                sektion=self.sektion)
            kat = get_kategorie(self.jahr, ein_mann)
            if alter < 15:
                self.assertEquals(self.kat_I, kat)
            elif alter < 18:
                self.assertEquals(self.kat_II, kat)
            elif alter < 21:
                self.assertEquals(self.kat_III, kat)
            elif alter < 43:
                self.assertEquals(self.kat_C, kat)
            else:
                self.assertEquals(self.kat_D, kat)

    def testFrauAlleJahre(self):
        for alter in range(1,100):
            jahrgang = self.jahr - alter
            eine_frau = Mitglied.objects.create(
                nummer=alter, name="Nina", vorname="Meier", geschlecht="f",
                geburtsdatum=datetime.date(jahrgang, 1, 1),
                sektion=self.sektion)
            kat = get_kategorie(self.jahr, eine_frau)
            if alter < 15:
                self.assertEquals(self.kat_I, kat)
            else:
                self.assertEquals(self.kat_F, kat)


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

    def testKatIIIandD(self):
        self._assert_kat(self.kat_C, self.kat_III, self.kat_D)

    def testUnbekannteKombination(self):
        self._assert_kat(None, self.kat_II, self.kat_C)
        self._assert_kat(None, self.kat_I, self.kat_D)
        self._assert_kat(None, self.kat_I, self.kat_F)
