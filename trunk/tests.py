# -*- coding: utf-8 -*-

import datetime

from django.core.urlresolvers import reverse
from django.test import TestCase

import views
import models

class WettkampfFormTest(TestCase):
    def setUp(self):
        # Fülle Datenbank mit einigen älteren Wettkämpfen
        models.Wettkampf.objects.create(name="Test-Cup", von="2003-04-04")
        models.Wettkampf.objects.create(name="Test-Cup", von="2005-04-04")
        models.Wettkampf.objects.create(name="Test-Cup", von="2007-04-04")
        # Gültiger Wettkampf
        self.form = views.WettkampfForm(data={
            'name': 'Test-Cup',
            'zusatz': 'Irgendwo',
            'von': '2009-04-10',
            'bis': '2009-04-11',
            })

    def test_valid(self):
        self.failUnless(self.form.is_valid(), self.form.errors)

    def test_invalid_name(self):
        self.form.data['name'] = u'Fällbaum Cup'
        nameError = self.form.errors.get('name')
        self.failIf(nameError is None)
        self.assertEquals(nameError[0], views.invalid_name_message)

    def test_earlier_bis_than_von(self):
        self.form.data['bis'] = '2009-04-09'
        nonFieldErrors = self.form.non_field_errors()
        self.failIf(len(nonFieldErrors) == 0)
        self.assertEquals(nonFieldErrors[0], u"Von muss älter als bis sein")

    def test_duplicate_name_for_new_wettkampf(self):
        self.form.data['von'] = '2007-01-01'
        nonFieldErrors = self.form.non_field_errors()
        self.failIf(len(nonFieldErrors) == 0)
        self.assertEquals(nonFieldErrors[0], u"Der Name 'Test-Cup' ist im Jahr '2007' bereits vergeben")

    def test_duplicate_name_for_existing_wettkampf(self):
        w2009 = self.form.save()
        self.form = views.WettkampfForm(data={
            'name': w2009.name,
            'zusatz': 'Ein anderer Zusatz',
            'von': str(w2009.von),
            }, instance=w2009)
        self.failUnless(self.form.is_valid(), self.form.errors)


class WettkampfTest(TestCase):

    def test_complete_scenario(self):

        response = self.client.get(reverse(views.wettkaempfe_get))
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.get('/add/')
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.post('/add/', {
            'name': 'Test-Cup',
            'zusatz': 'Bremgarten',
            'von': '2009-05-20',
            })
        self.assertRedirects(response, '/2009/Test-Cup/')

        response = self.client.get('/2009/Test-Cup/update/')
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.post('/2009/Test-Cup/update/', {
            'name': 'Test-Cup-Changed',
            'zusatz': 'Bremgarten',
            'von': '2009-05-20',
            })
        self.assertRedirects(response, '/2009/Test-Cup-Changed/')
        response = self.client.post('/2009/Test-Cup-Changed/update/', {
            'name': 'Test-Cup',
            'zusatz': 'Bremgarten',
            'von': '2009-05-20',
            })

        response = self.client.get('/')
        self.assertContains(response, 'Test-Cup')

        response = self.client.get('/2009/Test-Cup/add/')
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.post('/2009/Test-Cup/add/', {
            'wettkampf': response.context[-1]['wettkampf'].id,
            'name': u'automatisch-gefüllt',
            'disziplinart': 1,
            'kategorien': [1, 2],
            })
        self.assertRedirects(response, '/2009/Test-Cup/')

        response = self.client.get('/2009/Test-Cup/')
        self.assertContains(response, 'Einzelfahren-I-II')

        response = self.client.get('/2009/Test-Cup/Einzelfahren-I-II/')
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.get('/2009/Test-Cup/delete/')
        self.failUnlessEqual(response.status_code, 200)
        response = self.client.post('/2009/Test-Cup/delete/')
        self.assertRedirects(response, '/')
