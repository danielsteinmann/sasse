# -*- coding: utf-8 -*-

import datetime
import unittest
from decimal import Decimal

from django.test import TestCase
from django.forms import ValidationError

from sasse.fields import ZeitInSekundenField
from sasse.fields import StartnummernSelectionField
from sasse.models import Disziplin
from sasse.models import Schiffeinzel

class StartnummernSelectionFieldTest(TestCase):
    def setUp(self):
        # Rauschen einfügen, um die vollständige where clause zu prüfen
        d = Disziplin.objects.create(wettkampf_id=1, name="Eine-Disziplin")
        for startnr in range(1,50):
          Schiffeinzel.objects.create(startnummer=startnr, disziplin=d,
              steuermann_id=1, vorderfahrer_id=2, sektion_id=1, kategorie_id=1)
        d = Disziplin.objects.create(wettkampf_id=1, name="Test")
        for startnr in range(1,50):
          Schiffeinzel.objects.create(startnummer=startnr, disziplin=d,
              steuermann_id=1, vorderfahrer_id=2, sektion_id=1, kategorie_id=1)
        self.sut = StartnummernSelectionField(d)

    def test_invalid_input(self):
        value = '1-x'
        self.assertRaises(ValidationError, self.sut.clean, value)
        value = '-'
        self.assertRaises(ValidationError, self.sut.clean, value)
        value = '1-5,3--'
        self.assertRaises(ValidationError, self.sut.clean, value)
        value = 'z'
        self.assertRaises(ValidationError, self.sut.clean, value)

    def test_single_numbers(self):
        self.sut.clean('1,2,5')
        self.assertEquals(['1', '2', '5'], self.sut.startnummern_list)

    def test_full_range(self):
        self.sut.clean('3-6')
        self.assertEquals([3, 4, 5, 6], self.sut.startnummern_list)

    def test_open_ended_range(self):
        self.sut.clean('47-')
        self.assertEquals([47, 48, 49], self.sut.startnummern_list)

    def test_open_starting_range(self):
        self.sut.clean('-6')
        self.assertEquals([1, 2, 3, 4, 5, 6], self.sut.startnummern_list)


class ZeitInSekundenFieldTest(unittest.TestCase):
    def setUp(self):
        self.sut = ZeitInSekundenField()

    def test_invalid_input(self):
        value = 'x'
        self.assertRaises(ValidationError, self.sut.clean, value)
        value = ''
        self.assertRaises(ValidationError, self.sut.clean, value)
        value = None
        self.assertRaises(ValidationError, self.sut.clean, value)

    def test_minutes_seconds(self):
        value = '3:30'
        self.assertEquals(Decimal('210'), self.sut.clean(value))
        value = '3 30'
        self.assertEquals(Decimal('210'), self.sut.clean(value))
        value = '10 193'
        self.assertEquals(Decimal('793'), self.sut.clean(value))
        value = '3m30'
        self.assertRaises(ValidationError, self.sut.clean, value)

    def test_seconds_hundreds(self):
        value = '10.3'
        self.assertEquals(Decimal(value), self.sut.clean(value))
        value = '3.35'
        self.assertEquals(Decimal(value), self.sut.clean(value))

    def test_minutes_seconds_hundreds(self):
        value = '1:33.98'
        self.assertEquals(Decimal('93.98'), self.sut.clean(value))
        value = '1 33.98'
        self.assertEquals(Decimal('93.98'), self.sut.clean(value))
        value = '1 70.98'
        self.assertEquals(Decimal('130.98'), self.sut.clean(value))
        value = '1.33.98'
        self.assertEquals(Decimal('93.98'), self.sut.clean(value))
        value = '1:70:98'
        self.assertRaises(ValidationError, self.sut.clean, value)

    def test_seconds(self):
        value = '10'
        self.assertEquals(Decimal(value), self.sut.clean(value))
        value = '7'
        self.assertEquals(Decimal(value), self.sut.clean(value))
