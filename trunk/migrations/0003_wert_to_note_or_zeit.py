# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from sasse.models import *

class Migration:
    
    def forwards(self, orm):
        for b in orm.Bewertung.objects.select_related('bewertungsart').all():
            if b.bewertungsart.einheit == 'ZEIT':
                b.zeit = b.wert
            else:
                b.note = b.wert
            b.save()
    
    
    def backwards(self, orm):
        for b in orm.Bewertung.objects.select_related('bewertungsart').all():
            if b.bewertungsart.einheit == 'ZEIT':
                b.wert = b.zeit
            else:
                b.wert = b.note
            b.save()
    
    
    models = {
        'sasse.bewertung': {
            'Meta': {'unique_together': "(('teilnehmer', 'posten', 'bewertungsart'),)"},
            'bewertungsart': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Bewertungsart']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '1'}),
            'posten': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Posten']"}),
            'teilnehmer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Teilnehmer']"}),
            'wert': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'zeit': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'})
        },
        'sasse.bewertungsart': {
            'defaultwert': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'einheit': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'postenart': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Postenart']"}),
            'reihenfolge': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'signum': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'wertebereich': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'sasse.disziplin': {
            'Meta': {'unique_together': "(['wettkampf', 'name'],)"},
            'disziplinart': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['sasse.Disziplinart']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kategorien': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sasse.Kategorie']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'wettkampf': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Wettkampf']"})
        },
        'sasse.disziplinart': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'sasse.gruppe': {
            'chef': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Mitglied']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'sektion': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Sektion']"}),
            'teilnehmer_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sasse.Teilnehmer']", 'unique': 'True', 'primary_key': 'True'})
        },
        'sasse.kategorie': {
            'alter_bis': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'alter_von': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'disziplinart': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Disziplinart']"}),
            'geschlecht': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'sasse.kranzlimite': {
            'disziplin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Disziplin']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kategorie': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Kategorie']"}),
            'wert': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'})
        },
        'sasse.mitglied': {
            'geburtsdatum': ('django.db.models.fields.DateField', [], {}),
            'geschlecht': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'nummer': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Mitglied']", 'null': 'True'}),
            'sektion': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Sektion']"}),
            'vorname': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'sasse.person': {
            'kategorie': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Kategorie']"}),
            'mitglied': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Mitglied']"}),
            'sektion': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Sektion']"}),
            'teilnehmer_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sasse.Teilnehmer']", 'unique': 'True', 'primary_key': 'True'})
        },
        'sasse.posten': {
            'Meta': {'unique_together': "(['disziplin', 'name'],)"},
            'disziplin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Disziplin']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'postenart': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Postenart']"}),
            'reihenfolge': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'sasse.postenart': {
            'disziplinarten': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sasse.Disziplinart']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'sasse.richtzeit': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'posten': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Posten']"}),
            'zeit': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'})
        },
        'sasse.schiffeinzel': {
            'kategorie': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Kategorie']"}),
            'schiffsart': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'sektion': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Sektion']"}),
            'steuermann': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'steuermann'", 'to': "orm['sasse.Mitglied']"}),
            'teilnehmer_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sasse.Teilnehmer']", 'unique': 'True', 'primary_key': 'True'}),
            'vorderfahrer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'vorderfahrer'", 'to': "orm['sasse.Mitglied']"})
        },
        'sasse.schiffsektion': {
            'Meta': {'unique_together': "(['gruppe', 'position'],)"},
            'gruppe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Gruppe']"}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'schiffsart': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'teilnehmer_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sasse.Teilnehmer']", 'unique': 'True', 'primary_key': 'True'})
        },
        'sasse.sektion': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'sasse.teilnehmer': {
            'Meta': {'unique_together': "(('disziplin', 'startnummer'),)"},
            'ausgeschieden': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'disqualifiziert': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'disziplin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Disziplin']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'startnummer': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'sasse.wettkampf': {
            'bis': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'von': ('django.db.models.fields.DateField', [], {}),
            'zusatz': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }
    
    complete_apps = ['sasse']
