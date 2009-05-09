# -*- coding: utf-8 -*-

import datetime
import unittest

from django.core.urlresolvers import reverse
from django.test import TestCase

import views
from views import WettkampfForm
from models import Wettkampf
from models import Disziplinart
from models import Kategorie

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
        expected = views.invalid_name_message
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
        listURL = reverse(views.wettkaempfe_get)
        response = self.client.get(listURL)
        self.failUnlessEqual(response.status_code, 200)
        self.assertContains(response, 'Basis-Cup')
        self.failUnlessEqual(len(response.context[-1]['wettkaempfe']), 3)

    def test_list_by_year(self):
        listURL = reverse(views.wettkaempfe_by_year, args=['2008'])
        response = self.client.get(listURL)
        self.failUnlessEqual(response.status_code, 200)
        self.failUnlessEqual(response.context[-1]['year'], '2008')
        self.failUnlessEqual(len(response.context[-1]['wettkaempfe']), 2)

    def test_add(self):
        addURL = reverse(views.wettkaempfe_add)
        response = self.client.get(addURL)
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.post(addURL, {})
        self.assertContains(response, 'This field is required')
        response = self.client.post(addURL, {
            'name': 'Test-Cup',
            'zusatz': 'Bremgarten',
            'von': '2009-05-20',
            })
        getURL = reverse(views.wettkampf_get, args=['2009', 'Test-Cup'])
        self.assertRedirects(response, getURL)

    def test_update(self):
        updateURL = reverse(views.wettkampf_update, args=['2009', 'Basis-Cup'])
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
        getURL = reverse(views.wettkampf_get, args=['2008', 'New-Cup'])
        self.assertRedirects(response, getURL)

    def test_delete(self):
        deleteURL = reverse(views.wettkampf_delete_confirm,
                args=['2009', 'Basis-Cup'])
        response = self.client.get(deleteURL)
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.post(deleteURL)
        listURL = reverse(views.wettkaempfe_get)
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


class get_startkatgorie_Test(unittest.TestCase):
    def setUp(self):
        self.kat_I = Kategorie.objects.get(name='I')
        self.kat_II = Kategorie.objects.get(name='II')
        self.kat_III = Kategorie.objects.get(name='III')
        self.kat_C = Kategorie.objects.get(name='C')
        self.kat_D = Kategorie.objects.get(name='D')
        self.kat_F = Kategorie.objects.get(name='F')

    def _assert_kat(self, expected, a, b):
        self.assertEquals(expected, views.get_startkategorie(a, b))
        self.assertEquals(expected, views.get_startkategorie(b, a))

    def testGleicheKategorie(self):
        for k in Kategorie.objects.all():
            self.assertEquals(k, views.get_startkategorie(k, k))

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
