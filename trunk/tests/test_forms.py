# -*- coding: utf-8 -*-

import datetime
from decimal import Decimal

from django.test import TestCase

from sasse.forms import WettkampfForm
from sasse.forms import DisziplinForm
from sasse.forms import BewertungForm
from sasse.forms import PostenblattFilterForm

from sasse.models import Disziplinart
from sasse.models import Bewertungsart
from sasse.models import Kategorie
from sasse.models import Mitglied
from sasse.models import Postenart
from sasse.models import Schiffeinzel
from sasse.models import Sektion
from sasse.models import Wettkampf
from sasse.models import Disziplin

from sasse.fields import UnicodeSlugField


class WettkampfFormTest(TestCase):
    def setUp(self):
        # Fülle Datenbank mit einigen älteren Wettkämpfen
        Wettkampf.objects.create(name="Test-Cup", von="2003-04-04")
        Wettkampf.objects.create(name="Test-Cup", von="2005-04-04")
        Wettkampf.objects.create(name="Test-Cup", von="2007-04-04")
        # Gültiger Wettkampf
        self.sut = WettkampfForm(data={
            'name': 'Test-Cup',
            'zusatz': 'Irgendwo',
            'von': '2009-04-10',
            'bis': '2009-04-11',
            })

    def test_valid(self):
        self.failUnless(self.sut.is_valid(), self.sut.errors)

    def test_invalid_name(self):
        self.sut.data['name'] = u'No Spaces'
        self.failUnless(self.sut.errors.has_key('name'))
        expected = UnicodeSlugField.default_error_messages['invalid']
        self.failUnless(expected in self.sut.errors['name'])

    def test_earlier_bis_than_von(self):
        self.sut.data['bis'] = '2009-04-09'
        expected = u"Von muss älter als bis sein"
        self.failUnless(expected in self.sut.non_field_errors())

    def test_duplicate_name_for_new_wettkampf(self):
        self.sut.data['von'] = '2007-01-01'
        expected = u"Der Name 'Test-Cup' ist im Jahr '2007' bereits vergeben"
        self.failUnless(expected in self.sut.non_field_errors())

    def test_duplicate_name_for_existing_wettkampf(self):
        w2009 = self.sut.save()
        update_form = WettkampfForm(data={
            'name': 'Test-Cup',
            'zusatz': 'Ein anderer Zusatz',
            'von': '2007-01-01'
            }, instance=w2009)
        expected = u"Der Name 'Test-Cup' ist im Jahr '2007' bereits vergeben"
        self.failUnless(expected in update_form.non_field_errors())

    def test_update_existing_wettkampf(self):
        w2009 = self.sut.save()
        update_form = WettkampfForm(data={
            'name': w2009.name,
            'zusatz': 'Ein anderer Zusatz',
            'von': str(w2009.von),
            }, instance=w2009)
        self.failUnless(update_form.is_valid(), update_form.errors)


class DisziplinFormTest(TestCase):
    def setUp(self):
        wettkampf = Wettkampf.objects.create(
                name="Test-Cup",
                zusatz="Bremgarten",
                von="2009-04-04"
                )
        art = Disziplinart.objects.get(name="Einzelfahren")
        self.sut = DisziplinForm(wettkampf, data={
            'name': 'Einzelfahren-I',
            'disziplinart': art.id
            })

    def test_valid(self):
        self.failUnless(self.sut.is_valid(), self.sut.errors)

    def test_invalid_name(self):
        self.sut.data['name'] = u'Spaces Not Allowed'
        self.failUnless(self.sut.errors.has_key('name'))
        expected = UnicodeSlugField.default_error_messages['invalid']
        self.failUnless(expected in self.sut.errors['name'])

    def test_default_name(self):
        art = Disziplinart.objects.get(name="Einzelfahren")
        k1 = Kategorie.objects.get(name='I')
        k2 = Kategorie.objects.get(name='II')
        self.sut.data['name'] = DisziplinForm.INITIAL_NAME
        self.sut.data['kategorien'] = (k1.id, k2.id)
        self.failUnless(self.sut.is_valid(), self.sut.errors)
        self.assertEquals(self.sut.data['name'], "Einzelfahren-I-II")

    def test_duplicate_name_for_new_disziplin(self):
        saved_disziplin = self.sut.save()
        newform = DisziplinForm(saved_disziplin.wettkampf, data={
            'name': saved_disziplin.name,
            'disziplinart': saved_disziplin.id,
            })
        expected = u"Disziplin with this Wettkampf and Name already exists."
        errors = newform.non_field_errors()
        self.failUnless(expected in errors, errors)

    def test_duplicate_name_for_existing_disziplin(self):
        saved_disziplin = self.sut.save()
        new_disziplin = DisziplinForm(saved_disziplin.wettkampf, data={
            'name': 'neuer-name',
            'disziplinart': saved_disziplin.id,
            }).save()
        newform = DisziplinForm(saved_disziplin.wettkampf, data={
            'name': saved_disziplin.name,
            'disziplinart': saved_disziplin.id,
            }, instance=new_disziplin)
        expected = u"Disziplin with this Wettkampf and Name already exists."
        errors = newform.non_field_errors()
        self.failUnless(expected in errors, errors)

    def test_update_existing_disziplin(self):
        saved_disziplin = self.sut.save()
        newform = DisziplinForm(saved_disziplin.wettkampf, data={
            'name': 'some-new-name',
            'disziplinart': saved_disziplin.id,
            }, instance=saved_disziplin)
        self.failUnless(self.sut.is_valid(), self.sut.errors)


class BewertungFormTest(TestCase):
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
                name="Allgemeines und Antreten")
        self.antreten_abzug = Bewertungsart.objects.create(postenart=antreten,
                name="Abzug", signum=-1, einheit="PUNKT",
                wertebereich="0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10",
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
                bewertungsart=self.antreten_abzug,
                teilnehmer_id=self.startnr_1.id, data={'wert': '1.0',})
        self.failUnless(form.is_valid(), form.errors)
        b = form.save()
        # Die IDs müssen richtig verdrahtet sein
        self.assertEquals(self.startnr_1.startnummer, b.teilnehmer.startnummer)
        self.assertEquals(self.posten_a, b.posten)
        self.assertEquals(self.antreten_abzug, b.bewertungsart)

    def test_invalid_wert(self):
        form = BewertungForm(posten=self.posten_a,
                bewertungsart=self.antreten_abzug,
                teilnehmer_id=self.startnr_1.id, data={'wert': '1.9',})
        self.failUnless(form.errors.has_key('wert'))

    def test_default_wert(self):
        form = BewertungForm(posten=self.posten_a,
                bewertungsart=self.antreten_abzug,
                teilnehmer_id=self.startnr_1.id)
        expected = self.antreten_abzug.defaultwert
        self.assertEquals(expected, form.initial.get('wert'))

    def test_signum(self):
        create_form = BewertungForm(posten=self.posten_a,
                bewertungsart=self.antreten_abzug,
                teilnehmer_id=self.startnr_1.id, data={'wert': '1.0',})
        self.failUnless(create_form.is_valid(), create_form.errors)
        saved = create_form.save()
        self.assertEquals(+1, saved.note)
        edit_form = BewertungForm(posten=self.posten_a,
                bewertungsart=self.antreten_abzug,
                teilnehmer_id=self.startnr_1.id,
                initial={'id': saved.id, 'wert': saved.note,})
        self.assertEquals(+1, edit_form.initial['wert'])


class PostenblattFilterFormTest(TestCase):
    def setUp(self):
        d = Disziplin.objects.create(wettkampf_id=1, name="Test")
        for startnr in range(1, 10):
            Schiffeinzel.objects.create(startnummer=startnr, disziplin=d,
                    steuermann_id=1, vorderfahrer_id=2, sektion_id=1,
                    kategorie_id=1)
        self.sut = PostenblattFilterForm(d, data={'startnummern': '1,2,3'})

    def test_valid_input(self):
        self.failUnless(self.sut.is_valid(), self.sut.errors)

    def test_invalid_input(self):
        self.sut.data['startnummern'] = 'x'
        self.failIf(self.sut.is_valid())

    def test_selected_startnummern_no_input(self):
        self.sut.data['startnummern'] = ''
        self.sut.is_valid()
        actual = self.sut.selected_startnummern(visible=5)
        self.assertEquals(5, actual.count())

    def test_selected_startnummern_more_than_visible(self):
        self.sut.data['startnummern'] = '1,2,3,4,5,6'
        self.sut.is_valid()
        actual = self.sut.selected_startnummern(visible=2)
        self.assertEquals(2, actual.count())

    def test_selected_startnummern_less_than_visible(self):
        self.sut.data['startnummern'] = '1,2,3,4,5,6'
        self.sut.is_valid()
        actual = self.sut.selected_startnummern(visible=10)
        self.assertEquals(6, actual.count())
