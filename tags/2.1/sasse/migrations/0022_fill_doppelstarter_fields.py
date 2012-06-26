# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from django.db import connection
from django.template.loader import render_to_string
from sasse.models import Disziplin
from sasse.models import Schiffeinzel

class Migration(DataMigration):

    def forwards(self, orm):
        cursor = connection.cursor()
        sql = """
select * from (
    select tn.startnummer as Startnr
         , case when (
              select min(t.startnummer) normale_startnummer
                from sasse_mitglied m
                     join sasse_schiffeinzel schiff on (
                      schiff.vorderfahrer_id = m.id or schiff.steuermann_id = m.id)
                     join sasse_teilnehmer t on (t.id = schiff.teilnehmer_ptr_id)
               where m.id = max(hinten.id) and t.disziplin_id = max(tn.disziplin_id)
           ) = tn.startnummer then 0 else 1 end as SteuermannIstDS
         , case when (
              select min(t.startnummer) normale_startnummer
                from sasse_mitglied m
                     join sasse_schiffeinzel schiff on (
                      schiff.vorderfahrer_id = m.id or schiff.steuermann_id = m.id)
                     join sasse_teilnehmer t on (t.id = schiff.teilnehmer_ptr_id)
               where m.id = max(vorne.id) and t.disziplin_id = max(tn.disziplin_id)
           ) = tn.startnummer then 0 else 1 end as VorderfahrerIstDS
      from sasse_teilnehmer tn
      join sasse_schiffeinzel schiff on (schiff.teilnehmer_ptr_id = tn.id)
      join bewertung_calc b on (b.teilnehmer_id = tn.id)
      join sasse_kategorie kat on (kat.id = schiff.kategorie_id)
      join sasse_sektion sektion on (sektion.id = schiff.sektion_id)
      join sasse_mitglied vorne on (vorne.id = schiff.vorderfahrer_id)
      join sasse_mitglied hinten on (hinten.id = schiff.steuermann_id)
     where tn.disziplin_id = %s
     group by tn.startnummer
   ) as r
 where r.SteuermannIstDS = 1 or r.VorderfahrerIstDS = 1
             """
        for disziplin in Disziplin.objects.all():
            cursor.execute(sql, [disziplin.id])
            for row in cursor:
                startnr = row[0]
                hinten_ds = row[1]
                vorne_ds = row[2]
                s = Schiffeinzel.objects.get(disziplin=disziplin, startnummer=startnr)
                s.steuermann_ist_ds = hinten_ds
                s.vorderfahrer_ist_ds = vorne_ds
                s.save()

    def backwards(self, orm):
        "Write your backwards methods here."
        # Nothing to do
        pass


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
            'Meta': {'ordering': "['postenart', 'reihenfolge']", 'object_name': 'Bewertungsart'},
            'defaultwert': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '1'}),
            'editierbar': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'einheit': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'gruppe': ('django.db.models.fields.CharField', [], {'default': "'ZIEL'", 'max_length': '6'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'postenart': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Postenart']"}),
            'reihenfolge': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'signum': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'wertebereich': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'sasse.disziplin': {
            'Meta': {'ordering': "['name']", 'unique_together': "(['wettkampf', 'name'],)", 'object_name': 'Disziplin'},
            'disziplinart': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['sasse.Disziplinart']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kategorien': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sasse.Kategorie']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'wettkampf': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Wettkampf']"})
        },
        'sasse.disziplinart': {
            'Meta': {'object_name': 'Disziplinart'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'sasse.gruppe': {
            'Meta': {'ordering': "['startnummer']", 'object_name': 'Gruppe', '_ormbases': ['sasse.Teilnehmer']},
            'chef': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Mitglied']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'sektion': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Sektion']"}),
            'teilnehmer_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sasse.Teilnehmer']", 'unique': 'True', 'primary_key': 'True'})
        },
        'sasse.kategorie': {
            'Meta': {'ordering': "['reihenfolge']", 'object_name': 'Kategorie'},
            'alter_bis': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'alter_von': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'disziplinart': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Disziplinart']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'reihenfolge': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'})
        },
        'sasse.kranzlimite': {
            'Meta': {'object_name': 'Kranzlimite'},
            'disziplin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Disziplin']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kategorie': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Kategorie']"}),
            'wert': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '1'})
        },
        'sasse.mitglied': {
            'Meta': {'ordering': "['name', 'vorname', 'sektion']", 'object_name': 'Mitglied'},
            'geburtsdatum': ('django.db.models.fields.DateField', [], {}),
            'geschlecht': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'nummer': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '5'}),
            'sektion': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Sektion']"}),
            'vorname': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'sasse.person': {
            'Meta': {'ordering': "['startnummer']", 'object_name': 'Person', '_ormbases': ['sasse.Teilnehmer']},
            'kategorie': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Kategorie']"}),
            'mitglied': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Mitglied']"}),
            'sektion': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Sektion']"}),
            'teilnehmer_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sasse.Teilnehmer']", 'unique': 'True', 'primary_key': 'True'})
        },
        'sasse.posten': {
            'Meta': {'ordering': "['reihenfolge', 'name']", 'unique_together': "(['disziplin', 'name'],)", 'object_name': 'Posten'},
            'disziplin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Disziplin']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'postenart': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Postenart']"}),
            'reihenfolge': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'sasse.postenart': {
            'Meta': {'ordering': "['name']", 'object_name': 'Postenart'},
            'disziplinarten': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sasse.Disziplinart']", 'symmetrical': 'False'}),
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
            'Meta': {'ordering': "['startnummer']", 'object_name': 'Schiffeinzel', '_ormbases': ['sasse.Teilnehmer']},
            'kategorie': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Kategorie']"}),
            'sektion': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Sektion']"}),
            'steuermann': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'steuermann'", 'to': "orm['sasse.Mitglied']"}),
            'steuermann_ist_ds': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'teilnehmer_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sasse.Teilnehmer']", 'unique': 'True', 'primary_key': 'True'}),
            'vorderfahrer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'vorderfahrer'", 'to': "orm['sasse.Mitglied']"}),
            'vorderfahrer_ist_ds': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'sasse.schiffsektion': {
            'Meta': {'ordering': "['gruppe', 'position']", 'unique_together': "(['gruppe', 'position'],)", 'object_name': 'Schiffsektion', '_ormbases': ['sasse.Teilnehmer']},
            'gruppe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Gruppe']"}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'schiffsart': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'teilnehmer_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sasse.Teilnehmer']", 'unique': 'True', 'primary_key': 'True'})
        },
        'sasse.sektion': {
            'Meta': {'ordering': "['name']", 'object_name': 'Sektion'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'nummer': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2'})
        },
        'sasse.teilnehmer': {
            'Meta': {'ordering': "['startnummer']", 'unique_together': "(('disziplin', 'startnummer'),)", 'object_name': 'Teilnehmer'},
            'ausgeschieden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'disqualifiziert': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'disziplin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Disziplin']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'startnummer': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'sasse.wettkampf': {
            'JPSM': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'Meta': {'ordering': "['-von']", 'object_name': 'Wettkampf'},
            'bis': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'von': ('django.db.models.fields.DateField', [], {}),
            'zusatz': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['sasse']
