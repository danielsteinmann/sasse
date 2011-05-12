# -*- coding: utf-8 -*-

from decimal import Decimal

from django.test import TestCase
from django.db import connection
from django.template.loader import render_to_string

from sasse.models import Wettkampf
from sasse.models import Disziplin
from sasse.models import Postenart
from sasse.models import Kategorie
from sasse.models import Schiffeinzel
from sasse.models import Kranzlimite
from sasse.views import read_rangliste, sort_rangliste


class ZeitInPunkteTest(TestCase):
    """
    Testet die Konversion von der Zeit in Punkte.
    """
    def test_gleich_wie_richtzeit(self):
        richtzeit = Decimal("60.0")
        zeitwert = richtzeit
        self.assertEquals(Decimal("10.0"), self.z2p(zeitwert, richtzeit))

    def test_dreifache_richtzeit(self):
        richtzeit = Decimal("60.0")
        zeitwert = 3 * richtzeit
        self.assertEquals(0, self.z2p(zeitwert, richtzeit))

    def test_mehr_als_dreifach(self):
        richtzeit = Decimal("60.0")
        zeitwert = 3 * richtzeit + Decimal("10")
        self.assertEquals(0, self.z2p(zeitwert, richtzeit))

    def test_neun_komma_fuenf(self):
        richtzeit = Decimal("60.0")
        zeitwert = Decimal("66.0")
        self.assertEquals(Decimal("9.5"), self.z2p(zeitwert, richtzeit))

    def test_neun_komma_neun(self):
        richtzeit = Decimal("100.0")
        zeitwert = Decimal("102.0")
        self.assertEquals(Decimal("9.9"), self.z2p(zeitwert, richtzeit))

    def test_mehr_als_zehn(self):
        richtzeit = Decimal("60.0")
        zeitwert = Decimal("48.0")
        self.assertEquals(Decimal("11.0"), self.z2p(zeitwert, richtzeit))

    def z2p(self, zeitwert, richtzeit):
        zeitnote = Postenart.objects.get(name="Zeitnote")
        zeit = zeitnote.bewertungsart_set.all()[0]
        w = Wettkampf.objects.create(name="Test-Cup", von="2009-04-04")
        d = w.disziplin_set.create(name="Einzelfahren")
        p = d.posten_set.create(name="B-C", postenart=zeitnote, reihenfolge=1)
        t = d.teilnehmer_set.create(startnummer="1")
        p.richtzeit_set.create(zeit=richtzeit)
        t.bewertung_set.create(zeit=zeitwert, posten=p, bewertungsart=zeit)
        cursor = connection.cursor()
        cursor.execute("""
            select zeit, note, richtzeit
              from bewertung_calc
             where teilnehmer_id = %s and posten_id = %s
              """, [t.id, p.id])
        list = cursor.fetchall()
        self.assertEquals(1, len(list))
        (zeitwert, punktwert, richtzeit) = list[0]
        result = punktwert
        if not isinstance(result, Decimal):
            # SQLLite liefert keinen Decimal zurück, MySQL aber schon
            result = Decimal(str(result))
        return result


class RanglisteTest(TestCase):
    """
    Testet die Erstellung der Rangliste.

    1  Foo/Bar
    2  Hans/Wurst
    2  Gleicher/Rang
    4  Dritter/Rang
    DS Der/Doppler
    DS Nochein/Doppler
    ----- Kranzlimite -----
    5  Der/Vierte
    6  Noch/Einer
    DS Hans/Doppel
    -  Foo/Bar      disqualifiziert
    """
    fixtures = ['test_rangliste.json']

    def test_rangliste(self):
        disziplin = Disziplin.objects.get(
                name="Einzelfahren-II-III-C-D-F",
                wettkampf__name="Fällbaum-Cup",
                wettkampf__von__year="2010")
        kat_C = Kategorie.objects.get(name='C')
        cursor = connection.cursor()
        RANGLISTE = render_to_string('rangliste.sql', {'kategorie': kat_C})

        # Ohne Doppelstarter
        sql = "select * from (" + RANGLISTE + ") where SteuermannIstDS = 0 and VorderfahrerIstDS = 0"
        cursor.execute(sql, [disziplin.id, kat_C.id])
        self.assertEquals(10, len(cursor.fetchall()))

        # Nur Doppelstarter
        sql = "select * from (" + RANGLISTE + ") where SteuermannIstDS = 1 or VorderfahrerIstDS = 1"
        cursor.execute(sql, [disziplin.id, kat_C.id])
        self.assertEquals(3, len(cursor.fetchall()))

        # Komplett
        rangliste = read_rangliste(disziplin, kat_C)
        self.assertEquals(13, len(list(rangliste)))

        # Annotierte Rangliste
        actual = []
        for row in read_rangliste(disziplin, kat_C):
            actual.append(dict(rang=row['rang'], kranz=row['kranz'],
                doppelstarter=row['doppelstarter'], startnummer=row['startnummer']))
        expected = [
                {'rang':    1, 'kranz': True,  'doppelstarter': False, 'startnummer':  14},
                {'rang': 'DS', 'kranz': True,  'doppelstarter':  True, 'startnummer': 102},
                {'rang':    2, 'kranz': True,  'doppelstarter': False, 'startnummer':   2},
                {'rang':    3, 'kranz': True,  'doppelstarter': False, 'startnummer':  10},
                {'rang': 'DS', 'kranz': False, 'doppelstarter':  True, 'startnummer': 101},
                {'rang':    4, 'kranz': False, 'doppelstarter': False, 'startnummer':  12},
                {'rang':    5, 'kranz': False, 'doppelstarter': False, 'startnummer':   3},
                {'rang':    6, 'kranz': False, 'doppelstarter': False, 'startnummer':  11},
                {'rang':    7, 'kranz': False, 'doppelstarter': False, 'startnummer':   1},
                {'rang': 'DS', 'kranz': False, 'doppelstarter':  True, 'startnummer': 103},
                {'rang':    8, 'kranz': False, 'doppelstarter': False, 'startnummer':  13},
                {'rang':    9, 'kranz': False, 'doppelstarter': False, 'startnummer':   6},
                {'rang':'DISQ', 'kranz': False, 'doppelstarter': False, 'startnummer':   9},
                ]
        self.assertEquals(expected, actual)

        # Sortierte Rangliste
        actual = []
        rangliste = read_rangliste(disziplin, kat_C)
        for row in sorted(rangliste, key=sort_rangliste):
            actual.append(dict(rang=row['rang'], kranz=row['kranz'],
                doppelstarter=row['doppelstarter'], startnummer=row['startnummer']))
        expected = [
                {'rang':    1, 'kranz': True,  'doppelstarter': False, 'startnummer':  14},
                {'rang':    2, 'kranz': True,  'doppelstarter': False, 'startnummer':   2},
                {'rang':    3, 'kranz': True,  'doppelstarter': False, 'startnummer':  10},
                {'rang': 'DS', 'kranz': True,  'doppelstarter':  True, 'startnummer': 102},
                {'rang':    4, 'kranz': False, 'doppelstarter': False, 'startnummer':  12},
                {'rang':    5, 'kranz': False, 'doppelstarter': False, 'startnummer':   3},
                {'rang':    6, 'kranz': False, 'doppelstarter': False, 'startnummer':  11},
                {'rang':    7, 'kranz': False, 'doppelstarter': False, 'startnummer':   1},
                {'rang':    8, 'kranz': False, 'doppelstarter': False, 'startnummer':  13},
                {'rang':    9, 'kranz': False, 'doppelstarter': False, 'startnummer':   6},
                {'rang': 'DS', 'kranz': False, 'doppelstarter':  True, 'startnummer': 101},
                {'rang': 'DS', 'kranz': False, 'doppelstarter':  True, 'startnummer': 103},
                {'rang':'DISQ', 'kranz': False, 'doppelstarter': False, 'startnummer':   9},
                ]
        self.assertEquals(expected, actual)

        # Doppelstarter nicht separat ausgewiesen
        actual = []
        for row in read_rangliste(disziplin, kat_C, doppelstarter_mit_rang=True):
            actual.append(dict(rang=row['rang'], kranz=row['kranz'],
                doppelstarter=row['doppelstarter'], startnummer=row['startnummer']))
        expected = [
                {'rang':    1, 'kranz': True,  'doppelstarter': False, 'startnummer':  14},
                {'rang':    2, 'kranz': True,  'doppelstarter':  True, 'startnummer': 102},
                {'rang':    3, 'kranz': True,  'doppelstarter': False, 'startnummer':   2},
                {'rang':    4, 'kranz': True,  'doppelstarter': False, 'startnummer':  10},
                {'rang':    5, 'kranz': False, 'doppelstarter':  True, 'startnummer': 101},
                {'rang':    6, 'kranz': False, 'doppelstarter': False, 'startnummer':  12},
                {'rang':    7, 'kranz': False, 'doppelstarter': False, 'startnummer':   3},
                {'rang':    8, 'kranz': False, 'doppelstarter': False, 'startnummer':  11},
                {'rang':    9, 'kranz': False, 'doppelstarter': False, 'startnummer':   1},
                {'rang':   10, 'kranz': False, 'doppelstarter':  True, 'startnummer': 103},
                {'rang':   11, 'kranz': False, 'doppelstarter': False, 'startnummer':  13},
                {'rang':   12, 'kranz': False, 'doppelstarter': False, 'startnummer':   6},
                {'rang':'DISQ', 'kranz': False, 'doppelstarter': False, 'startnummer':   9},
                ]
        self.assertEquals(expected, actual)
