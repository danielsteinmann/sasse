# -*- coding: utf-8 -*-

import datetime
import unittest
from decimal import Decimal

from django.test import TestCase
from django.forms import ValidationError

from sasse.fields import UnicodeSlugField
from sasse.fields import MitgliedSearchField
from sasse.fields import ZeitInSekundenField
from sasse.fields import StartnummernSelectionField
from sasse.models import Disziplin
from sasse.models import Schiffeinzel
from sasse.models import Sektion
from sasse.models import Mitglied

class UnicodeSlugFieldTest(TestCase):
    def setUp(self):
        self.sut = UnicodeSlugField()

    def test_invalid_input(self):
        self.assertRaises(ValidationError, self.sut.clean, None)
        self.assertRaises(ValidationError, self.sut.clean, '')
        self.assertRaises(ValidationError, self.sut.clean, u'Fällbaum Cup')
        self.assertRaises(ValidationError, self.sut.clean, u' Fällbaum-Cup')

    def test_valid(self):
        name = u'Fällbaum-Cup'
        self.assertEquals(name, self.sut.clean(name))


class MitgliedSearchFieldTest(TestCase):
    def setUp(self):
        bremgarten = Sektion.objects.get(name="Bremgarten")
        self.steinmann_daniel = Mitglied.objects.create(nummer="101",
                name="Steinmann", vorname="Daniel", geschlecht="m",
                geburtsdatum=datetime.date(1967, 4, 30), sektion=bremgarten)
        self.steinmann_omar = Mitglied.objects.create(nummer="102",
                name="Steinmann", vorname="Omar", geschlecht="m",
                geburtsdatum=datetime.date(1967, 4, 30), sektion=bremgarten)
        self.kohler = Mitglied.objects.create(nummer="103",
                name="Kohler", vorname="Bernhard", geschlecht="m",
                geburtsdatum=datetime.date(1978, 1, 1), sektion=bremgarten)
        self.sut = MitgliedSearchField(queryset=Mitglied.objects.all())

    def test_invalid_input(self):
        self.assertRaises(ValidationError, self.sut.clean, '')
        self.assertRaises(ValidationError, self.sut.clean, None)

    def test_nummer(self):
        nummer = self.steinmann_daniel.nummer
        self.assertEquals(self.steinmann_daniel, self.sut.clean(nummer))
        nummer = self.kohler.nummer
        self.assertEquals(self.kohler, self.sut.clean(nummer))

    def test_id(self):
        id = str(self.steinmann_daniel.id)
        self.assertEquals(self.steinmann_daniel, self.sut.clean(id))
        id = str(self.kohler.id)
        self.assertEquals(self.kohler, self.sut.clean(id))

    def test_name(self):
        name = "Kohler"
        self.assertEquals(self.kohler, self.sut.clean(name))

    def test_name_vorname(self):
        name = "Steinmann Daniel"
        self.assertEquals(self.steinmann_daniel, self.sut.clean(name))

    def test_partial_name_vorname(self):
        name = "Stein Dan"
        self.assertEquals(self.steinmann_daniel, self.sut.clean(name))
        name = "st da"
        self.assertEquals(self.steinmann_daniel, self.sut.clean(name))

    def test_unknown(self):
        self.assertRaises(ValidationError, self.sut.clean, 'xxx')

    def test_not_unique(self):
        self.assertRaises(ValidationError, self.sut.clean, 'steinmann')
        self.assertEquals(2, self.sut.queryset.count())


class StartnummernSelectionFieldTest(TestCase):
    def setUp(self):
        # Rauschen einfügen, um die vollständige where clause zu prüfen
        d = Disziplin.objects.create(wettkampf_id=1, name="Eine-Disziplin")
        for startnr in range(1,50):
          Schiffeinzel.objects.create(startnummer=startnr, disziplin=d,
              steuermann_id=1, vorderfahrer_id=2, sektion_id=1, kategorie_id=1)
        # Eine Grundmenge Teilnehmer einfügen
        d = Disziplin.objects.create(wettkampf_id=1, name="Test")
        for startnr in range(1,50):
          Schiffeinzel.objects.create(startnummer=startnr, disziplin=d,
              steuermann_id=1, vorderfahrer_id=2, sektion_id=1, kategorie_id=1)
        self.sut = StartnummernSelectionField(d)

    def test_invalid_input(self):
        self.assertRaises(ValidationError, self.sut.clean, '1-x')
        self.assertRaises(ValidationError, self.sut.clean, '-')
        self.assertRaises(ValidationError, self.sut.clean, '1-5,3--')
        self.assertRaises(ValidationError, self.sut.clean, 'z')
        self.assertRaises(ValidationError, self.sut.clean, ',')

    def test_no_input(self):
        self.sut.clean('')
        self.assertEquals([], self.sut.startnummern_list)
        self.sut.clean(' ')
        self.assertEquals([], self.sut.startnummern_list)

    def test_single_numbers(self):
        self.sut.clean('1,2,5')
        self.assertEquals([1, 2, 5], self.sut.startnummern_list)

    def test_input_with_spaces(self):
        self.sut.clean(' 1, 2 ,5 ')
        self.assertEquals([1, 2, 5], self.sut.startnummern_list)

    def test_unordered_single_numbers(self):
        self.sut.clean('1,3,2')
        self.assertEquals([1, 3, 2], self.sut.startnummern_list)

    def test_single_and_range(self):
        self.sut.clean('1,2,5-7,9')
        self.assertEquals([1, 2, 5, 6, 7, 9], self.sut.startnummern_list)

    def test_full_range(self):
        self.sut.clean('3-6')
        self.assertEquals([3, 4, 5, 6], self.sut.startnummern_list)

    def test_open_ending_range(self):
        self.sut.clean('47-')
        self.assertEquals([47, 48, 49], self.sut.startnummern_list)

    def test_open_starting_range(self):
        self.sut.clean('-6')
        self.assertEquals([1, 2, 3, 4, 5, 6], self.sut.startnummern_list)


class ZeitInSekundenFieldTest(unittest.TestCase):
    def setUp(self):
        self.sut = ZeitInSekundenField()

    def test_invalid_input(self):
        self.assertRaises(ValidationError, self.sut.clean, 'x')
        self.assertRaises(ValidationError, self.sut.clean, '')
        self.assertRaises(ValidationError, self.sut.clean, ' ')
        self.assertRaises(ValidationError, self.sut.clean, None)
        self.assertRaises(ValidationError, self.sut.clean, '3m30')
        self.assertRaises(ValidationError, self.sut.clean, '1:70:98')
        self.assertRaises(ValidationError, self.sut.clean, '0')
        self.assertRaises(ValidationError, self.sut.clean, '0:0.0')

    def test_minutes_seconds(self):
        self.assertEquals(Decimal('210'), self.sut.clean('3:30'))
        self.assertEquals(Decimal('210'), self.sut.clean('3 30'))
        self.assertEquals(Decimal('210'), self.sut.clean('3 30'))
        self.assertEquals(Decimal('793'), self.sut.clean('10 193'))

    def test_seconds_hundreds(self):
        self.assertEquals(Decimal('10.3'), self.sut.clean('10.3'))
        self.assertEquals(Decimal('3.35'), self.sut.clean('3.35'))
        self.assertEquals(Decimal('3.357'), self.sut.clean('3.357'))

    def test_minutes_seconds_hundreds(self):
        self.assertEquals(Decimal('93.98'), self.sut.clean('1:33.98'))
        self.assertEquals(Decimal('93.98'), self.sut.clean('1 33.98'))
        self.assertEquals(Decimal('130.98'), self.sut.clean('1 70.98'))
        self.assertEquals(Decimal('93.98'), self.sut.clean('1.33.98'))
        self.assertEquals(Decimal('93.987'), self.sut.clean('1.33.987'))

    def test_seconds(self):
        self.assertEquals(Decimal('10'), self.sut.clean('10'))
        self.assertEquals(Decimal('7'), self.sut.clean('7'))
