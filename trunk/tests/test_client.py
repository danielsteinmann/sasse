# -*- coding: utf-8 -*-

import datetime
import unittest

from django.core.urlresolvers import reverse
from django.test import TestCase

from sasse.views import wettkaempfe_get
from sasse.views import wettkaempfe_by_year
from sasse.views import wettkaempfe_add
from sasse.views import wettkampf_get
from sasse.views import wettkampf_update
from sasse.views import wettkampf_delete_confirm

from sasse.models import Disziplinart
from sasse.models import Kategorie
from sasse.models import Schiffeinzel
from sasse.models import Postenart
from sasse.models import Wettkampf
from sasse.models import Mitglied
from sasse.models import Sektion


class WettkampfPageTest(TestCase):

    def setUp(self):
        Wettkampf.objects.create(
                name="Basis-Cup",
                zusatz="Testingen",
                von="2009-04-30"
                )
        Wettkampf.objects.create(
                name="Eidgenössisches",
                zusatz="Woanders",
                von="2008-07-12"
                )
        Wettkampf.objects.create(
                name="Probewettkampf",
                zusatz="Im gleichen Jahr wie das Eidgenössische",
                von="2008-07-12"
                )

    def test_list(self):
        listURL = reverse(wettkaempfe_get)
        response = self.client.get(listURL)
        self.failUnlessEqual(response.status_code, 200)
        self.assertContains(response, 'Basis-Cup')
        self.failUnlessEqual(len(response.context[-1]['wettkaempfe']), 3)

    def test_list_by_year(self):
        listURL = reverse(wettkaempfe_by_year, args=['2008'])
        response = self.client.get(listURL)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context[-1]['year'], '2008')
        self.failUnlessEqual(len(response.context[-1]['wettkaempfe']), 2)

    def test_add(self):
        addURL = reverse(wettkaempfe_add)
        response = self.client.get(addURL)
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.post(addURL, {})
        self.assertContains(response, 'This field is required')
        response = self.client.post(addURL, {
            'name': 'Test-Cup',
            'zusatz': 'Bremgarten',
            'von': '2009-05-20',
            })
        getURL = reverse(wettkampf_get, args=['2009', 'Test-Cup'])
        self.assertRedirects(response, getURL)

    def test_update(self):
        updateURL = reverse(wettkampf_update, args=['2009', 'Basis-Cup'])
        response = self.client.get(updateURL)
        self.failUnlessEqual(response.status_code, 200)
        self.assertContains(response, 'Basis-Cup')
        response = self.client.post(updateURL, {})
        self.assertContains(response, 'This field is required')
        response = self.client.post(updateURL, {
            'name': 'New-Cup',
            'zusatz': 'Ein anderer Zusatz',
            'von': '2008-05-20',
            })
        getURL = reverse(wettkampf_get, args=['2008', 'New-Cup'])
        self.assertRedirects(response, getURL)

    def test_delete(self):
        deleteURL = reverse(wettkampf_delete_confirm,
                args=['2009', 'Basis-Cup'])
        response = self.client.get(deleteURL)
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.post(deleteURL)
        listURL = reverse(wettkaempfe_get)
        self.assertRedirects(response, listURL)
        response = self.client.get(listURL)
        self.assertNotContains(response, 'Basis-Cup')


class DisziplinPageTest(TestCase):

    def setUp(self):
        art = Disziplinart.objects.get(name="Einzelfahren")
        katI = Kategorie.objects.get(name="I")
        w = Wettkampf.objects.create(
                name="Test-Cup",
                zusatz="Bremgarten",
                von="2009-04-04"
                )
        d = w.disziplin_set.create(
                name="Einzelfahren-I",
                disziplinart=art,
                )
        d.kategorien.add(katI)

    def test_list(self):
        response = self.client.get('/2009/Test-Cup/')
        self.assertContains(response, 'Einzelfahren-I')

    def test_add(self):
        addURL = '/2009/Test-Cup/add/'
        response = self.client.get(addURL)
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.post(addURL, {})
        self.assertContains(response, 'This field is required')
        art = Disziplinart.objects.get(name="Einzelfahren")
        katI = Kategorie.objects.get(name="I")
        katII = Kategorie.objects.get(name="II")
        response = self.client.post(addURL, {
            'name': u'automatisch-gefüllt',
            'disziplinart': art.id,
            'kategorien': [katI.id, katII.id],
            })
        self.assertRedirects(response, '/2009/Test-Cup/')
        response = self.client.get('/2009/Test-Cup/Einzelfahren-I-II/')
        self.failUnlessEqual(response.status_code, 200)

    def test_update(self):
        updateURL = '/2009/Test-Cup/Einzelfahren-I/update/'
        response = self.client.post(updateURL, {})
        self.assertContains(response, 'This field is required')
        response = self.client.get(updateURL)
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.post(updateURL, {
            'name': 'Mein-Einzelfahren',
            'disziplinart': response.context[-1]['disziplin'].disziplinart.id,
            })
        self.assertRedirects(response, '/2009/Test-Cup/Mein-Einzelfahren/')

    def test_delete(self):
        listURL = '/2009/Test-Cup/'
        deleteURL = '/2009/Test-Cup/Einzelfahren-I/delete/'
        response = self.client.get(deleteURL)
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.post(deleteURL)
        self.assertRedirects(response, listURL)
        response = self.client.get(listURL)
        self.assertNotContains(response, 'Einzelfahren-I')


class PostenPageTest(TestCase):

    def setUp(self):
        einzel = Disziplinart.objects.get(name="Einzelfahren")
        w = Wettkampf.objects.create(name="Test-Cup", von="2009-04-04")
        d = w.disziplin_set.create(name="klein", disziplinart=einzel)
        d.kategorien.add(Kategorie.objects.get(name="I"))
        durchfahrt = Postenart.objects.get(name="Durchfahrt")
        p = d.posten_set.create(name="D", postenart=durchfahrt, reihenfolge=3)

    def test_list(self):
        response = self.client.get('/2009/Test-Cup/klein/posten/')
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(len(response.context[-1]['posten']), 1)

    def test_add(self):
        addURL = '/2009/Test-Cup/klein/posten/'
        response = self.client.get(addURL)
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.post(addURL, {})
        self.assertContains(response, 'This field is required')
        antreten = Postenart.objects.get(name="Allgemeines und Antreten (Einzelfahren)")
        response = self.client.post(addURL, {
            'name': u'A0',
            'postenart': antreten.id,
            })
        self.assertRedirects(response, addURL)
        response = self.client.get('/2009/Test-Cup/klein/posten/A0')
        self.failUnlessEqual(response.status_code, 200)

    def test_update(self):
        updateURL = '/2009/Test-Cup/klein/posten/D/update/'
        response = self.client.post(updateURL, {})
        self.assertContains(response, 'This field is required')
        response = self.client.get(updateURL)
        self.failUnlessEqual(response.status_code, 200)
        durchfahrt = Postenart.objects.get(name="Durchfahrt")
        response = self.client.post(updateURL, {
            'name': u'ZZ',
            'postenart': durchfahrt.id,
            'reihenfolge': '9',
            })
        self.assertRedirects(response, '/2009/Test-Cup/klein/posten/')

    def test_delete(self):
        listURL = '/2009/Test-Cup/klein/posten/'
        getURL = '/2009/Test-Cup/klein/posten/D'
        deleteURL = '/2009/Test-Cup/klein/posten/D/delete/'
        response = self.client.get(deleteURL)
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.post(deleteURL)
        self.assertRedirects(response, listURL)


class EinzelfahrenStartlistePageTest(TestCase):

    def setUp(self):
        einzel = Disziplinart.objects.get(name="Einzelfahren")
        w = Wettkampf.objects.create(name="Test-Cup", von="2009-04-04")
        d = w.disziplin_set.create(name="klein", disziplinart=einzel)
        d.kategorien.add(Kategorie.objects.get(name="I"))
        bremgarten = Sektion.objects.create(name="Bremgarten")
        Mitglied.objects.create(
                name="Steinmann", vorname="Daniel", geschlecht="m",
                geburtsdatum=datetime.date(1967, 4, 30),
                sektion=bremgarten)
        Mitglied.objects.create(
                name="Kohler", vorname="Bernhard", geschlecht="m",
                geburtsdatum=datetime.date(1978, 1, 1),
                sektion=bremgarten)

    def test_list(self):
        response = self.client.get('/2009/Test-Cup/klein/startliste/')
        self.failUnlessEqual(response.status_code, 200)

    def test_add(self):
        addURL = '/2009/Test-Cup/klein/startliste/'
        response = self.client.get(addURL)
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.post(addURL, {})
        self.assertContains(response, 'This field is required')
        response = self.client.post(addURL, {
            'startnummer': u'1',
            'steuermann': u'stein',
            'vorderfahrer': u'kohler b',
            })
        self.assertRedirects(response, addURL)
        response = self.client.get('/2009/Test-Cup/klein/startliste/')
        self.failUnlessEqual(response.status_code, 200)
        self.assertContains(response, 'Steinmann')

    def test_show_teilnehmer(self):
        addURL = '/2009/Test-Cup/klein/startliste/'
        response = self.client.post(addURL, {
            'startnummer': u'1',
            'steuermann': u'stein',
            'vorderfahrer': u'kohler b',
            })
        updateURL = '/2009/Test-Cup/klein/teilnehmer/1/'
        response = self.client.get(updateURL)
        self.assertContains(response, 'Steinmann')


class PostenblattPageTest(TestCase):
    def setUp(self):
        einzel = Disziplinart.objects.get(name="Einzelfahren")
        w = Wettkampf.objects.create(name="Test-Cup", von="2009-04-04")
        d = w.disziplin_set.create(name="klein", disziplinart=einzel)
        durchfahrt = Postenart.objects.get(name="Durchfahrt")
        posten_D = d.posten_set.create(name="D", postenart=durchfahrt,
                reihenfolge=1)
        posten_F = d.posten_set.create(name="F", postenart=durchfahrt,
                reihenfolge=2)
        for startnr in range(1,50):
            Schiffeinzel.objects.create(startnummer=startnr, disziplin=d,
                    steuermann_id=1, vorderfahrer_id=2, sektion_id=1,
                    kategorie_id=1)

    def test_bewertungen_redirect_to_postenblatt(self):
        bewertungen = '/2009/Test-Cup/klein/bewertungen/'
        postenblatt_D = '/2009/Test-Cup/klein/postenblatt/D/'
        response = self.client.get(bewertungen)
        self.assertRedirects(response, postenblatt_D)
        response = self.client.get(postenblatt_D)
        self.failUnlessEqual(response.status_code, 200)

    def test_filter_startnummern(self):
        postenblatt_D = '/2009/Test-Cup/klein/postenblatt/D/'
        # Default Anzahl Teilnehmer
        response = self.client.get(postenblatt_D)
        self.failUnlessEqual(response.status_code, 200)
        teilnehmer_count = len(response.context['startliste'].teilnehmer_forms())
        self.assertEquals(15, teilnehmer_count)
        # Gefilterte Anzahl Teilnehmer
        response = self.client.get(postenblatt_D, {'startnummern': '1,2'})
        self.failUnlessEqual(response.status_code, 200)
        teilnehmer_count = len(response.context['startliste'].teilnehmer_forms())
        self.assertEquals(2, teilnehmer_count)
        # Ungültiger Filter
        response = self.client.get(postenblatt_D, {'startnummern': 'XXX'})
        self.assertContains(response, 'Bitte nur ganze Zahlen, Bindestrich oder Komma eingeben')
        self.assertEquals(None, response.context['startliste'])

    def test_naechster_posten(self):
        postenblatt_D = '/2009/Test-Cup/klein/postenblatt/D/'
        postenblatt_F = '/2009/Test-Cup/klein/postenblatt/F/'
        response = self.client.get(postenblatt_D)
        self.failUnlessEqual(response.status_code, 200)
        self.assertEquals('F', response.context['posten_next_name'])
        response = self.client.get(postenblatt_F)
        self.failUnlessEqual(response.status_code, 200)
        self.assertEquals(None, response.context['posten_next_name'])

    def test_speichern_defaults(self):
        postenblatt_D = '/2009/Test-Cup/klein/postenblatt/D/'
        postenblatt_D_update = '/2009/Test-Cup/klein/postenblatt/D/update/'
        response = self.client.post(postenblatt_D_update, {
            'total': 2,
            'stnr-0-teilnehmer': 1,
            'stnr-1-teilnehmer': 2,
            'Abzug-TOTAL_FORMS': 2,
            'Abzug-INITIAL_FORMS': 0,
            'Abzug-0-wert': 0,
            'Abzug-1-wert': 0,
            'Note-TOTAL_FORMS': 2,
            'Note-INITIAL_FORMS': 0,
            'Note-0-wert': 10,
            'Note-1-wert': 10,
            })
        self.assertRedirects(response, postenblatt_D)
        response = self.client.get(postenblatt_D_update)
        self.failUnlessEqual(response.status_code, 200)

    def test_speichern_mit_ungueltigem_wert(self):
        postenblatt_D_update = '/2009/Test-Cup/klein/postenblatt/D/update/'
        response = self.client.post(postenblatt_D_update, {
            'total': 2,
            'stnr-0-teilnehmer': 1,
            'stnr-1-teilnehmer': 2,
            'Abzug-TOTAL_FORMS': 2,
            'Abzug-INITIAL_FORMS': 0,
            'Abzug-0-wert': '7.3',
            'Abzug-1-wert': 'xx',
            'Note-TOTAL_FORMS': 2,
            'Note-INITIAL_FORMS': 0,
            'Note-0-wert': 10,
            'Note-1-wert': 10,
            })
        self.failUnlessEqual(response.status_code, 200)
        self.assertContains(response, 'Nur ganze Zahlen oder Vielfaches von 0.5 erlaubt')

    def test_speichern_und_weiter(self):
        postenblatt_D_update = '/2009/Test-Cup/klein/postenblatt/D/update/'
        postenblatt_F_update = '/2009/Test-Cup/klein/postenblatt/F/update/'
        response = self.client.post(postenblatt_D_update, {
            'total': 2,
            'stnr-0-teilnehmer': 1,
            'stnr-1-teilnehmer': 2,
            'Abzug-TOTAL_FORMS': 2,
            'Abzug-INITIAL_FORMS': 0,
            'Abzug-0-wert': 0,
            'Abzug-1-wert': 0,
            'Note-TOTAL_FORMS': 2,
            'Note-INITIAL_FORMS': 0,
            'Note-0-wert': 10,
            'Note-1-wert': 10,
            'save_and_next': 'Blabla',
            'posten_next_name': 'F',
            })
        self.assertRedirects(response, postenblatt_F_update)
        response = self.client.get(postenblatt_F_update)
        self.failUnlessEqual(response.status_code, 200)

    def test_speichern_und_weiter_am_ende(self):
        postenblatt_D = '/2009/Test-Cup/klein/postenblatt/D/'
        postenblatt_F_update = '/2009/Test-Cup/klein/postenblatt/F/update/'
        response = self.client.post(postenblatt_F_update, {
            'total': 2,
            'stnr-0-teilnehmer': 1,
            'stnr-1-teilnehmer': 2,
            'Abzug-TOTAL_FORMS': 2,
            'Abzug-INITIAL_FORMS': 0,
            'Abzug-0-wert': 0,
            'Abzug-1-wert': 0,
            'Note-TOTAL_FORMS': 2,
            'Note-INITIAL_FORMS': 0,
            'Note-0-wert': 10,
            'Note-1-wert': 10,
            'save_and_finish': 'Blabla',
            })
        self.assertRedirects(response, postenblatt_D)

    def test_aendern_existierender_daten(self):
        postenblatt_D = '/2009/Test-Cup/klein/postenblatt/D/'
        postenblatt_D_update = '/2009/Test-Cup/klein/postenblatt/D/update/'
        response = self.client.post(postenblatt_D_update, {
            'total': 2,
            'stnr-0-teilnehmer': 1,
            'stnr-1-teilnehmer': 2,
            'Abzug-TOTAL_FORMS': 2,
            'Abzug-INITIAL_FORMS': 0,
            'Abzug-0-wert': 0,
            'Abzug-1-wert': 0,
            'Note-TOTAL_FORMS': 2,
            'Note-INITIAL_FORMS': 0,
            'Note-0-wert': 10,
            'Note-1-wert': 10,
            })
        self.assertRedirects(response, postenblatt_D)
        response = self.client.post(postenblatt_D_update, {
            'total': 2,
            'stnr-0-teilnehmer': 1,
            'stnr-1-teilnehmer': 2,
            'Abzug-TOTAL_FORMS': 2,
            'Abzug-INITIAL_FORMS': 0,
            'Abzug-0-wert': 0,
            'Abzug-0-id': 1,
            'Abzug-1-wert': 0,
            'Abzug-1-id': 2,
            'Note-TOTAL_FORMS': 2,
            'Note-INITIAL_FORMS': 0,
            'Note-0-wert': 10,
            'Note-0-id': 3,
            'Note-1-wert': 10,
            'Note-1-id': 4,
            })
        self.assertRedirects(response, postenblatt_D)

