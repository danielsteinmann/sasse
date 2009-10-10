# -*- coding: utf-8 -*-

import datetime
import unittest

from django.test import TestCase

from sasse.forms import get_kategorie
from sasse.forms import get_startkategorie
from sasse.forms import WettkampfForm
from sasse.forms import DisziplinForm

from sasse.models import Disziplinart
from sasse.models import Kategorie
from sasse.models import Wettkampf
from sasse.models import Mitglied
from sasse.models import Sektion

from sasse.fields import UnicodeSlugField


class WettkampfFormTest(TestCase):
    def setUp(self):
        # Fülle Datenbank mit einigen älteren Wettkämpfen
        Wettkampf.objects.create(name="Test-Cup", von="2003-04-04")
        Wettkampf.objects.create(name="Test-Cup", von="2005-04-04")
        Wettkampf.objects.create(name="Test-Cup", von="2007-04-04")
        # Gültiger Wettkampf
        self.form = WettkampfForm(data={
            'name': 'Test-Cup',
            'zusatz': 'Irgendwo',
            'von': '2009-04-10',
            'bis': '2009-04-11',
            })

    def test_valid(self):
        self.failUnless(self.form.is_valid(), self.form.errors)

    def test_invalid_name(self):
        self.form.data['name'] = u'No Spaces'
        self.failUnless(self.form.errors.has_key('name'))
        expected = UnicodeSlugField.default_error_messages['invalid']
        self.failUnless(expected in self.form.errors['name'])

    def test_earlier_bis_than_von(self):
        self.form.data['bis'] = '2009-04-09'
        expected = u"Von muss älter als bis sein"
        self.failUnless(expected in self.form.non_field_errors())

    def test_duplicate_name_for_new_wettkampf(self):
        self.form.data['von'] = '2007-01-01'
        expected = u"Der Name 'Test-Cup' ist im Jahr '2007' bereits vergeben"
        self.failUnless(expected in self.form.non_field_errors())

    def test_duplicate_name_for_existing_wettkampf(self):
        w2009 = self.form.save()
        self.form = WettkampfForm(data={
            'name': 'Test-Cup',
            'zusatz': 'Ein anderer Zusatz',
            'von': '2007-01-01'
            }, instance=w2009)
        expected = u"Der Name 'Test-Cup' ist im Jahr '2007' bereits vergeben"
        self.failUnless(expected in self.form.non_field_errors())

    def test_update_existing_wettkampf(self):
        w2009 = self.form.save()
        self.form = WettkampfForm(data={
            'name': w2009.name,
            'zusatz': 'Ein anderer Zusatz',
            'von': str(w2009.von),
            }, instance=w2009)
        self.failUnless(self.form.is_valid(), self.form.errors)


class DisziplinFormTest(TestCase):
    def setUp(self):
        wettkampf = Wettkampf.objects.create(
                name="Test-Cup",
                zusatz="Bremgarten",
                von="2009-04-04"
                )
        art = Disziplinart.objects.get(name="Einzelfahren")
        Disziplin.objects.create(name="Einzelfahren-test", disziplinart=art)
        self.form = DisziplinForm(wettkampf, data={
            'name': 'Einzelfahren-I',
            'disziplinart': art.id
            })

    def test_valid(self):
        self.failUnless(self.form.is_valid(), self.form.errors)

    def test_invalid_name(self):
        self.form.data['name'] = u'No Spaces'
        self.failUnless(self.form.errors.has_key('name'))
        expected = UnicodeSlugField.default_error_messages['invalid']
        self.failUnless(expected in self.form.errors['name'])

    def test_default_name(self):
        art = Disziplinart.objects.get(name="Einzelfahren")
        k1 = Kategorie.objects.get(name='I')
        k2 = Kategorie.objects.get(name='II')
        self.form.data['name'] = DisziplinForm.INITIAL_NAME
        self.form.data['kategorien'] = (k1.id, k2.id)
        self.failUnless(self.form.is_valid(), self.form.errors)
        self.assertEquals(self.form.data['name'], "Einzelfahren-I-II")

    def test_duplicate_name_for_new_disziplin(self):
        saved_disziplin = self.form.save()
        newform = DisziplinForm(saved_disziplin.wettkampf, data={
            'name': saved_disziplin.name,
            'disziplinart': saved_disziplin.id,
            })
        expected = u"Für den Wettkampf 'Test-Cup' ist der Name 'Einzelfahren-I' bereits vergeben"
        errors = newform.non_field_errors()
        self.failUnless(expected in errors, errors)

    def test_duplicate_name_for_existing_disziplin(self):
        saved_disziplin = self.form.save()
        new_disziplin = DisziplinForm(saved_disziplin.wettkampf, data={
            'name': 'neuer-name',
            'disziplinart': saved_disziplin.id,
            }).save()
        newform = DisziplinForm(saved_disziplin.wettkampf, data={
            'name': saved_disziplin.name,
            'disziplinart': saved_disziplin.id,
            }, instance=new_disziplin)
        expected = u"Für den Wettkampf 'Test-Cup' ist der Name 'Einzelfahren-I' bereits vergeben"
        errors = newform.non_field_errors()
        self.failUnless(expected in errors, errors)

    def test_update_existing_disziplin(self):
        saved_disziplin = self.form.save()
        newform = DisziplinForm(saved_disziplin.wettkampf, data={
            'name': 'some-new-name',
            'disziplinart': saved_disziplin.id,
            }, instance=saved_disziplin)
        self.failUnless(self.form.is_valid(), self.form.errors)

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
