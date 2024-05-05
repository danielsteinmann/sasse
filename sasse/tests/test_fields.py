# -*- coding: utf-8 -*-

import datetime
import unittest
from decimal import Decimal
from operator import attrgetter

from django.test import TestCase
from django.forms import ValidationError

from sasse.fields import UnicodeSlugField
from sasse.fields import MitgliedSearchField
from sasse.fields import PunkteField
from sasse.fields import ZeitInSekundenField
from sasse.fields import StartnummernSelectionField
from sasse.models import Disziplin
from sasse.models import Schiffeinzel
from sasse.models import Sektion
from sasse.models import Bewertungsart
from sasse.models import Mitglied
from sasse.templatetags.sasse import zeit2str

class UnicodeSlugFieldTest(TestCase):
    def setUp(self):
        self.sut = UnicodeSlugField()

    def test_invalid_input(self):
        self.assertRaises(ValidationError, self.sut.clean, None)
        self.assertRaises(ValidationError, self.sut.clean, '')
        self.assertRaises(ValidationError, self.sut.clean, 'Fällbaum Cup')
        self.assertRaises(ValidationError, self.sut.clean, ' Fällbaum-Cup')

    def test_valid(self):
        name = 'Fällbaum-Cup'
        self.assertEqual(name, self.sut.clean(name))


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
        self.assertEqual(self.steinmann_daniel, self.sut.clean(nummer))
        nummer = self.kohler.nummer
        self.assertEqual(self.kohler, self.sut.clean(nummer))

    def test_id(self):
        id = str(self.steinmann_daniel.id)
        self.assertEqual(self.steinmann_daniel, self.sut.clean(id))
        id = str(self.kohler.id)
        self.assertEqual(self.kohler, self.sut.clean(id))

    def test_name(self):
        name = "Kohler"
        self.assertEqual(self.kohler, self.sut.clean(name))

    def test_name_vorname(self):
        name = "Steinmann Daniel"
        self.assertEqual(self.steinmann_daniel, self.sut.clean(name))

    def test_partial_name_vorname(self):
        name = "Stein Dan"
        self.assertEqual(self.steinmann_daniel, self.sut.clean(name))
        name = "st da"
        self.assertEqual(self.steinmann_daniel, self.sut.clean(name))

    def test_unknown(self):
        self.assertRaises(ValidationError, self.sut.clean, 'xxx')

    def test_not_unique(self):
        self.assertRaises(ValidationError, self.sut.clean, 'steinmann')
        self.assertEqual(2, self.sut.queryset.count())


class StartnummernSelectionFieldTest(TestCase):
    def setUp(self):
        # Rauschen einfügen, um die vollständige where clause zu prüfen
        d = Disziplin.objects.create(wettkampf_id=1, name="Eine-Disziplin")
        for startnr in range(1,51):
            Schiffeinzel.objects.create(startnummer=startnr, disziplin=d,
                    steuermann_id=1, vorderfahrer_id=2, sektion_id=1,
                    kategorie_id=1)
        # Eine Grundmenge Teilnehmer einfügen
        d = Disziplin.objects.create(wettkampf_id=1, name="Test")
        for startnr in range(1,51):
            Schiffeinzel.objects.create(startnummer=startnr, disziplin=d,
                    steuermann_id=1, vorderfahrer_id=2, sektion_id=1,
                    kategorie_id=1)
        self.sut = StartnummernSelectionField(d)

    def _assertResult(self, user_input, expected_startnummern):
        qs = self.sut.clean(user_input)
        transform = attrgetter("startnummer")
        self.assertQuerysetEqual(qs, expected_startnummern, transform)

    def test_invalid_input(self):
        self.assertRaises(ValidationError, self.sut.clean, '1-x')
        self.assertRaises(ValidationError, self.sut.clean, '-')
        self.assertRaises(ValidationError, self.sut.clean, '1-5,3--')
        self.assertRaises(ValidationError, self.sut.clean, 'z')
        self.assertRaises(ValidationError, self.sut.clean, ',')

    def test_no_input(self):
        self.assertEqual(50, self.sut.clean('').count())
        self.assertEqual(50, self.sut.clean(' ').count())

    def test_single_numbers(self):
        self._assertResult('1,2,5', [1, 2, 5])

    def test_input_with_spaces(self):
        self._assertResult(' 1, 2 ,5 ', [1, 2, 5])

    # TODO: Reihenfolge beibehalten. 
    def todo_test_unordered_single_numbers(self):
        self._assertResult('1,3,2', [1, 3, 2])

    def test_single_and_range(self):
        self._assertResult('1,2,5-7,9', [1, 2, 5, 6, 7, 9])

    def test_full_range(self):
        self._assertResult('3-6', [3, 4, 5, 6])

    def test_open_ending_range(self):
        self._assertResult('47-', [47, 48, 49, 50])

    def test_open_starting_range(self):
        self._assertResult('-6', [1, 2, 3, 4, 5, 6])


class PunkteFieldTest(TestCase):
    def setUp(self):
        art = Bewertungsart.objects.create(postenart_id=1,
                name="Abzug", signum=-1, einheit="PUNKT",
                wertebereich="0, 1, 9.5, 10",
                defaultwert=3)
        self.sut = PunkteField(art)

    def test_invalid_input(self):
        self.assertRaises(ValidationError, self.sut.clean, 'x')
        self.assertRaises(ValidationError, self.sut.clean, '')
        self.assertRaises(ValidationError, self.sut.clean, '1,0')
        self.assertRaises(ValidationError, self.sut.clean, None)

    def test_min_and_below(self):
        self.assertEqual(Decimal('0'), self.sut.clean('0'))
        self.assertEqual(Decimal('0'), self.sut.clean('0.0'))
        self.assertRaises(ValidationError, self.sut.clean, '-1')

    def test_max_and_above(self):
        self.assertEqual(Decimal('10.0'), self.sut.clean('10'))
        self.assertRaises(ValidationError, self.sut.clean, '10.5')

    def test_normal_range(self):
        self.assertEqual(Decimal('1'), self.sut.clean('1'))
        self.assertEqual(Decimal('1'), self.sut.clean('1.0'))
        self.assertEqual(Decimal('9.5'), self.sut.clean('9.5'))

    def test_wrong_fractional_part(self):
        self.assertRaises(ValidationError, self.sut.clean, '1.8')


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
        self.assertEqual(Decimal('210'), self.sut.clean('3:30'))
        self.assertEqual(Decimal('210'), self.sut.clean('3 30'))
        self.assertEqual(Decimal('210'), self.sut.clean('3 30'))
        self.assertEqual(Decimal('793'), self.sut.clean('10 193'))

    def test_seconds_hundreds(self):
        self.assertEqual(Decimal('10.3'), self.sut.clean('10.3'))
        self.assertEqual(Decimal('3.35'), self.sut.clean('3.35'))
        self.assertEqual(Decimal('3.357'), self.sut.clean('3.357'))

    def test_minutes_seconds_hundreds(self):
        self.assertEqual(Decimal('93.98'), self.sut.clean('1:33.98'))
        self.assertEqual(Decimal('93.98'), self.sut.clean('1 33.98'))
        self.assertEqual(Decimal('130.98'), self.sut.clean('1 70.98'))
        self.assertEqual(Decimal('93.98'), self.sut.clean('1.33.98'))
        self.assertEqual(Decimal('93.987'), self.sut.clean('1.33.987'))

    def test_seconds(self):
        self.assertEqual(Decimal('10'), self.sut.clean('10'))
        self.assertEqual(Decimal('7'), self.sut.clean('7'))


class ZeitToStringTest(unittest.TestCase):
    def test_invalid_input(self):
        self.assertRaises(AssertionError, zeit2str, None)
        self.assertRaises(AssertionError, zeit2str, '')

    def test_seconds(self):
        self.assertEqual('0:00.00', zeit2str(Decimal('0')))
        self.assertEqual('0:01.00', zeit2str(Decimal('1')))
        self.assertEqual('1:03.00', zeit2str(Decimal('63')))
        self.assertEqual('1:15.00', zeit2str(Decimal('75')))

    def test_fractional_seconds(self):
        self.assertEqual('0:00.19', zeit2str(Decimal('.19')))
        self.assertEqual('0:01.87', zeit2str(Decimal('1.87')))
        self.assertEqual('1:03.87', zeit2str(Decimal('63.87')))
        self.assertEqual('1:03.01', zeit2str(Decimal('63.01')))
        self.assertEqual('2:25.80', zeit2str(Decimal('145.8')))
        self.assertEqual('2:25.87', zeit2str(Decimal('145.87')))
