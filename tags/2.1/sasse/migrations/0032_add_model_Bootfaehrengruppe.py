# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Bootfaehrengruppe'
        db.create_table('sasse_bootfaehrengruppe', (
            ('teilnehmer_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['sasse.Teilnehmer'], unique=True, primary_key=True)),
            ('sektion', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sasse.Sektion'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('kategorie', self.gf('django.db.models.fields.CharField')(default='Aktive', max_length=10)),
            ('zuschlaege', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=1)),
            ('einbauzeit', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=2)),
            ('ausbauzeit', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=2)),
            ('zeit', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=2)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('sasse', ['Bootfaehrengruppe'])


    def backwards(self, orm):
        
        # Deleting model 'Bootfaehrengruppe'
        db.delete_table('sasse_bootfaehrengruppe')


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
        'sasse.bootfaehrengruppe': {
            'Meta': {'ordering': "['startnummer']", 'object_name': 'Bootfaehrengruppe', '_ormbases': ['sasse.Teilnehmer']},
            'ausbauzeit': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'einbauzeit': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'kategorie': ('django.db.models.fields.CharField', [], {'default': "'Aktive'", 'max_length': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'sektion': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Sektion']"}),
            'teilnehmer_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sasse.Teilnehmer']", 'unique': 'True', 'primary_key': 'True'}),
            'zeit': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'zuschlaege': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '1'})
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
        'sasse.einzelschnuerer': {
            'Meta': {'ordering': "['startnummer']", 'object_name': 'Einzelschnuerer', '_ormbases': ['sasse.Teilnehmer']},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'kategorie': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'mitglied': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Mitglied']", 'unique': 'True'}),
            'parcourszeit': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'teilnehmer_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sasse.Teilnehmer']", 'unique': 'True', 'primary_key': 'True'}),
            'zeit': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'zuschlaege': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'})
        },
        'sasse.gruppe': {
            'Meta': {'ordering': "['name']", 'object_name': 'Gruppe', '_ormbases': ['sasse.Teilnehmer']},
            'abzug_gruppe': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '1', 'blank': 'True'}),
            'abzug_gruppe_comment': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'abzug_sektion': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '1', 'blank': 'True'}),
            'abzug_sektion_comment': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
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
            'ft1_steuermann': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ft1_steuermann'", 'to': "orm['sasse.Mitglied']"}),
            'ft1_vorderfahrer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ft1_vorderfahrer'", 'to': "orm['sasse.Mitglied']"}),
            'ft2_steuermann': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ft2_steuermann'", 'to': "orm['sasse.Mitglied']"}),
            'ft2_vorderfahrer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ft2_vorderfahrer'", 'to': "orm['sasse.Mitglied']"}),
            'gruppe': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Gruppe']"}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'teilnehmer_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sasse.Teilnehmer']", 'unique': 'True', 'primary_key': 'True'})
        },
        'sasse.schnuergruppe': {
            'Meta': {'ordering': "['startnummer']", 'object_name': 'Schnuergruppe', '_ormbases': ['sasse.Teilnehmer']},
            'abbauzeit': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'aufbauzeit': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'kategorie': ('django.db.models.fields.CharField', [], {'default': "'Aktive'", 'max_length': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'sektion': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Sektion']"}),
            'teilnehmer_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sasse.Teilnehmer']", 'unique': 'True', 'primary_key': 'True'}),
            'zeit': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'}),
            'zuschlaege': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '1'})
        },
        'sasse.schwimmer': {
            'Meta': {'ordering': "['startnummer']", 'object_name': 'Schwimmer', '_ormbases': ['sasse.Teilnehmer']},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'kategorie': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'mitglied': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Mitglied']", 'unique': 'True'}),
            'teilnehmer_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sasse.Teilnehmer']", 'unique': 'True', 'primary_key': 'True'}),
            'zeit': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'})
        },
        'sasse.sektion': {
            'Meta': {'ordering': "['name']", 'object_name': 'Sektion'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'nummer': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2'})
        },
        'sasse.sektionsfahrenkranzlimiten': {
            'Meta': {'object_name': 'SektionsfahrenKranzlimiten'},
            'ausser_konkurrenz': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Sektion']", 'null': 'True', 'blank': 'True'}),
            'disziplin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Disziplin']"}),
            'gold': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lorbeer': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '3'}),
            'silber': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '3'})
        },
        'sasse.spezialwettkaempfekranzlimite': {
            'Meta': {'object_name': 'SpezialwettkaempfeKranzlimite'},
            'disziplin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Disziplin']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kategorie': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'zeit': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'})
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
