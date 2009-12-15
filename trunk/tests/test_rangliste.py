# -*- coding: utf-8 -*-

from decimal import Decimal

from django.test import TestCase
from django.db import connection

from sasse.models import Wettkampf
from sasse.models import Postenart


class ZeitInPunkteTest(TestCase):
    """
    Testet die Konversion von der Zeit in Punkte.
    """
    def test_gleich_wie_richtzeit(self):
        richtzeit = Decimal("60.0")
        zeitwert = richtzeit
        self.assertEquals(Decimal("10.0"), self.z2p(zeitwert, richtzeit))

    def test_doppelte_richtzeit(self):
        richtzeit = Decimal("60.0")
        zeitwert = 2 * richtzeit
        self.assertEquals(0, self.z2p(zeitwert, richtzeit))

    def test_mehr_als_doppelt(self):
        richtzeit = Decimal("60.0")
        zeitwert = Decimal("130.0")
        self.assertEquals(0, self.z2p(zeitwert, richtzeit))

    def test_neun_komma_fuenf(self):
        richtzeit = Decimal("60.0")
        zeitwert = Decimal("63.0")
        self.assertEquals(Decimal("9.5"), self.z2p(zeitwert, richtzeit))

    def test_neun_komma_neun(self):
        richtzeit = Decimal("100.0")
        zeitwert = Decimal("101.0")
        self.assertEquals(Decimal("9.9"), self.z2p(zeitwert, richtzeit))

    def test_mehr_als_zehn(self):
        richtzeit = Decimal("60.0")
        zeitwert = Decimal("54.0")
        self.assertEquals(Decimal("11.0"), self.z2p(zeitwert, richtzeit))

    def z2p(self, zeitwert, richtzeit):
        zeitnote = Postenart.objects.get(name="Zeitnote")
        zeit = zeitnote.bewertungsart_set.all()[0]
        w = Wettkampf.objects.create(name="Test-Cup", von="2009-04-04")
        d = w.disziplin_set.create(name="Einzelfahren")
        p = d.posten_set.create(name="B-C", postenart=zeitnote, reihenfolge=1)
        t = d.teilnehmer_set.create(startnummer="1")
        p.richtzeit_set.create(zeit=richtzeit)
        t.bewertung_set.create(wert=zeitwert, posten=p, bewertungsart=zeit)
        cursor = connection.cursor()
        cursor.execute("""
            select zeitwert, richtzeit, punktwert
              from bewertung_in_punkte
             where teilnehmer_id = %s and posten_id = %s
              """, [t.id, p.id])
        list = cursor.fetchall()
        self.assertEquals(1, len(list))
        (zeitwert, richtzeit, punktwert) = list[0]
        result = punktwert
        if not isinstance(result, Decimal):
            # SQLLite liefert keinen Decimal zurück, MySQL aber schon
            result = Decimal(str(result))
        return result

