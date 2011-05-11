# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.db import connection

class Migration(SchemaMigration):
    no_dry_run = True
    
    def forwards(self, orm):
        cursor = connection.cursor()
        # File: templates/bewertung_in_punkte.sql
        sql = """
-- Alle Zeitbewertungen, konvertiert in Punkte
create view bewertung_in_punkte as
    select b.teilnehmer_id
         , b.posten_id
         , b.bewertungsart_id
         , b.zeit
         , case
             -- Umrechnung von Zeit zu Note
             when ba.einheit = 'ZEIT' then
               round(
                 case
                   when b.zeit > (2 * r.zeit) then 0
                   else 20.00 - (b.zeit / (r.zeit / 10.00))
                 end
               , 2)
             else
               b.note
           end as note
         , r.zeit as richtzeit
      from sasse_bewertung b
           join sasse_bewertungsart ba on (ba.id = b.bewertungsart_id)
           left outer join sasse_richtzeit r on (r.posten_id = b.posten_id)
"""
        cursor.execute(sql)
        # File: templates/doppelstarter.sql
        sql = """
-- Doppelstarter ist derjeninge mit der groesseren Startnummer
create view doppelstarter as
    select tn.disziplin_id
         , m.id mitglied_id
         , min(tn.startnummer) normale_startnummer
         , count(tn.id) anzahl_starts
      from sasse_mitglied m
           join sasse_schiffeinzel schiff on (
               schiff.vorderfahrer_id = m.id or schiff.steuermann_id = m.id)
           join sasse_teilnehmer tn on (tn.id = schiff.teilnehmer_ptr_id)
     group by tn.disziplin_id, m.id
    having count(tn.id) > 1
"""
        cursor.execute(sql)
    
    def backwards(self, orm):
        cursor = connection.cursor()
        for view in ['bewertung_in_punkte', 'doppelstarter']:
            cursor.execute("drop view %s" % view)
    
    
    models = {
        'sasse.bewertung': {
            'Meta': {'unique_together': "(('teilnehmer', 'posten', 'bewertungsart'),)", 'object_name': 'Bewertung'},
            'bewertungsart': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Bewertungsart']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '1'}),
            'posten': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Posten']"}),
            'teilnehmer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Teilnehmer']"}),
            'zeit': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'})
        },
        'sasse.bewertungsart': {
            'Meta': {'object_name': 'Bewertungsart'},
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
            'Meta': {'unique_together': "(['wettkampf', 'name'],)", 'object_name': 'Disziplin'},
            'disziplinart': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['sasse.Disziplinart']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kategorien': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sasse.Kategorie']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'wettkampf': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Wettkampf']"})
        },
        'sasse.disziplinart': {
            'Meta': {'object_name': 'Disziplinart'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'sasse.gruppe': {
            'Meta': {'object_name': 'Gruppe', '_ormbases': ['sasse.Teilnehmer']},
            'chef': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Mitglied']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'sektion': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Sektion']"}),
            'teilnehmer_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sasse.Teilnehmer']", 'unique': 'True', 'primary_key': 'True'})
        },
        'sasse.kategorie': {
            'Meta': {'object_name': 'Kategorie'},
            'alter_bis': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'alter_von': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'disziplinart': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Disziplinart']"}),
            'geschlecht': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'sasse.kranzlimite': {
            'Meta': {'object_name': 'Kranzlimite'},
            'disziplin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Disziplin']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kategorie': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Kategorie']"}),
            'wert': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'})
        },
        'sasse.mitglied': {
            'Meta': {'object_name': 'Mitglied'},
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
            'Meta': {'object_name': 'Person', '_ormbases': ['sasse.Teilnehmer']},
            'kategorie': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Kategorie']"}),
            'mitglied': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Mitglied']"}),
            'sektion': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Sektion']"}),
            'teilnehmer_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sasse.Teilnehmer']", 'unique': 'True', 'primary_key': 'True'})
        },
        'sasse.posten': {
            'Meta': {'unique_together': "(['disziplin', 'name'],)", 'object_name': 'Posten'},
            'disziplin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Disziplin']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'postenart': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Postenart']"}),
            'reihenfolge': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'sasse.postenart': {
            'Meta': {'object_name': 'Postenart'},
            'disziplinarten': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sasse.Disziplinart']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'sasse.richtzeit': {
            'Meta': {'object_name': 'Richtzeit'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'posten': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Posten']"}),
            'zeit': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'})
        },
        'sasse.schiffeinzel': {
            'Meta': {'object_name': 'Schiffeinzel', '_ormbases': ['sasse.Teilnehmer']},
            'kategorie': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Kategorie']"}),
            'schiffsart': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'sektion': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Sektion']"}),
            'steuermann': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'steuermann'", 'to': "orm['sasse.Mitglied']"}),
            'teilnehmer_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sasse.Teilnehmer']", 'unique': 'True', 'primary_key': 'True'}),
            'vorderfahrer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'vorderfahrer'", 'to': "orm['sasse.Mitglied']"})
        },
        'sasse.schiffsektion': {
            'Meta': {'unique_together': "(['gruppe', 'position'],)", 'object_name': 'Schiffsektion', '_ormbases': ['sasse.Teilnehmer']},
            'gruppe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Gruppe']"}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'schiffsart': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'teilnehmer_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sasse.Teilnehmer']", 'unique': 'True', 'primary_key': 'True'})
        },
        'sasse.sektion': {
            'Meta': {'object_name': 'Sektion'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'sasse.teilnehmer': {
            'Meta': {'unique_together': "(('disziplin', 'startnummer'),)", 'object_name': 'Teilnehmer'},
            'ausgeschieden': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'disqualifiziert': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'disziplin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Disziplin']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'startnummer': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'sasse.wettkampf': {
            'Meta': {'object_name': 'Wettkampf'},
            'bis': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'von': ('django.db.models.fields.DateField', [], {}),
            'zusatz': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }
    
    complete_apps = ['sasse']
