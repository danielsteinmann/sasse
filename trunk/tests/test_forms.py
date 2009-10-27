# -*- coding: utf-8 -*-

import datetime
from decimal import Decimal

from django.test import TestCase

from sasse.forms import WettkampfForm
from sasse.forms import DisziplinForm
from sasse.forms import BewertungForm

from sasse.models import Disziplinart
from sasse.models import Bewertungsart
from sasse.models import Kategorie
from sasse.models import Mitglied
from sasse.models import Postenart
from sasse.models import Schiffeinzel
from sasse.models import Sektion
from sasse.models import Wettkampf

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
        expected = u"Disziplin with this Wettkampf and Namen already exists."
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
        expected = u"Disziplin with this Wettkampf and Namen already exists."
        errors = newform.non_field_errors()
        self.failUnless(expected in errors, errors)

    def test_update_existing_disziplin(self):
        saved_disziplin = self.form.save()
        newform = DisziplinForm(saved_disziplin.wettkampf, data={
            'name': 'some-new-name',
            'disziplinart': saved_disziplin.id,
            }, instance=saved_disziplin)
        self.failUnless(self.form.is_valid(), self.form.errors)


class BewertungFormTest(TestCase):
    """
    Formset für eine Liste von Startnummern.  Das Postenblatt besteht aus 1-n
    solchen Formsets.  Gibt man 'einzelfahren/postenblatt/' ein, also keine
    konkreten Parameter, dann wird der erste Posten mit den ersten 15
    Startnummern gezeigt.
    """
    def setUp(self):
        # Stammdaten
        bremgarten = Sektion.objects.get(name="Bremgarten")
        steinmann = Mitglied.objects.create(
                name="Steinmann", vorname="Daniel", geschlecht="m",
                geburtsdatum=datetime.date(1967, 4, 30),
                sektion=bremgarten)
        kohler = Mitglied.objects.create(
                name="Kohler", vorname="Bernhard", geschlecht="m",
                geburtsdatum=datetime.date(1978, 1, 1),
                sektion=bremgarten)
        kat_C = Kategorie.objects.get(name="C")
        einzelfahren = Disziplinart.objects.get(name="Einzelfahren")
        antreten = Postenart.objects.get(
                name="Allgemeines und Antreten (Einzelfahren)")
        self.antreten_abzug = Bewertungsart.objects.create(postenart=antreten,
                name="Abzug", signum=-1, einheit="PUNKT", wertebereich="1,2,3",
                defaultwert=3)
        # Bewegungsdaten
        testcup = Wettkampf.objects.create(name="Test-Cup",
                zusatz="Bremgarten", von="2009-04-04")
        einzel = testcup.disziplin_set.create(name="gross",
                disziplinart=einzelfahren)
        self.startnr_1 = Schiffeinzel.objects.create(startnummer=1,
                steuermann=steinmann, vorderfahrer=kohler, sektion=bremgarten,
                kategorie=kat_C, disziplin=einzel)
        self.posten_a = einzel.posten_set.create(name="A", postenart=antreten,
                reihenfolge=1)

    def test_valid(self):
        form = BewertungForm(posten=self.posten_a,
                bewertungsart=self.antreten_abzug, data={'wert': '1.0',
                    'teilnehmer': self.startnr_1.id,})
        self.failUnless(form.is_valid(), form.errors)
        b = form.save()
        # Die IDs müssen richtig verdrahtet sein
        self.assertEquals(self.startnr_1.startnummer, b.teilnehmer.startnummer)
        self.assertEquals(self.posten_a, b.posten)
        self.assertEquals(self.antreten_abzug, b.bewertungsart)

    def test_valid_halbe_zahl(self):
        form = BewertungForm(posten=self.posten_a,
                bewertungsart=self.antreten_abzug, data={'wert': '1.5',
                    'teilnehmer': self.startnr_1.id,})
        self.failUnless(form.is_valid(), form.errors)

    def test_invalid_wert(self):
        form = BewertungForm(posten=self.posten_a,
                bewertungsart=self.antreten_abzug, data={'wert': '1.9',
                    'teilnehmer': self.startnr_1.id,})
        self.failUnless(form.errors.has_key('wert'))

    def test_default_wert(self):
        form = BewertungForm(posten=self.posten_a,
                bewertungsart=self.antreten_abzug, data={'teilnehmer':
                    self.startnr_1.id,})
        expected = self.antreten_abzug.defaultwert
        self.assertEquals(expected, form.initial.get('wert'))

    def test_signum(self):
        create_form = BewertungForm(posten=self.posten_a,
                bewertungsart=self.antreten_abzug, data={'wert': '1.0',
                    'teilnehmer': self.startnr_1.id,})
        self.failUnless(create_form.is_valid(), create_form.errors)
        saved = create_form.save()
        self.assertEquals(-1, saved.wert)
        edit_form = BewertungForm(posten=self.posten_a,
                bewertungsart=self.antreten_abzug, initial={'id': saved.id,
                    'wert': saved.wert,})
        self.assertEquals(+1, edit_form.initial['wert'])

