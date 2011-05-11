# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from sasse.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Sektion'
        db.create_table('sasse_sektion', (
            ('id', orm['sasse.Sektion:id']),
            ('name', orm['sasse.Sektion:name']),
        ))
        db.send_create_signal('sasse', ['Sektion'])
        
        # Adding model 'Posten'
        db.create_table('sasse_posten', (
            ('id', orm['sasse.Posten:id']),
            ('disziplin', orm['sasse.Posten:disziplin']),
            ('name', orm['sasse.Posten:name']),
            ('postenart', orm['sasse.Posten:postenart']),
            ('reihenfolge', orm['sasse.Posten:reihenfolge']),
        ))
        db.send_create_signal('sasse', ['Posten'])
        
        # Adding model 'Wettkampf'
        db.create_table('sasse_wettkampf', (
            ('id', orm['sasse.Wettkampf:id']),
            ('name', orm['sasse.Wettkampf:name']),
            ('zusatz', orm['sasse.Wettkampf:zusatz']),
            ('von', orm['sasse.Wettkampf:von']),
            ('bis', orm['sasse.Wettkampf:bis']),
        ))
        db.send_create_signal('sasse', ['Wettkampf'])
        
        # Adding model 'Richtzeit'
        db.create_table('sasse_richtzeit', (
            ('id', orm['sasse.Richtzeit:id']),
            ('posten', orm['sasse.Richtzeit:posten']),
            ('zeit', orm['sasse.Richtzeit:zeit']),
        ))
        db.send_create_signal('sasse', ['Richtzeit'])
        
        # Adding model 'Mitglied'
        db.create_table('sasse_mitglied', (
            ('id', orm['sasse.Mitglied:id']),
            ('nummer', orm['sasse.Mitglied:nummer']),
            ('name', orm['sasse.Mitglied:name']),
            ('vorname', orm['sasse.Mitglied:vorname']),
            ('geburtsdatum', orm['sasse.Mitglied:geburtsdatum']),
            ('geschlecht', orm['sasse.Mitglied:geschlecht']),
            ('sektion', orm['sasse.Mitglied:sektion']),
            ('parent', orm['sasse.Mitglied:parent']),
        ))
        db.send_create_signal('sasse', ['Mitglied'])
        
        # Adding model 'Disziplin'
        db.create_table('sasse_disziplin', (
            ('id', orm['sasse.Disziplin:id']),
            ('wettkampf', orm['sasse.Disziplin:wettkampf']),
            ('name', orm['sasse.Disziplin:name']),
            ('disziplinart', orm['sasse.Disziplin:disziplinart']),
        ))
        db.send_create_signal('sasse', ['Disziplin'])
        
        # Adding model 'Bewertung'
        db.create_table('sasse_bewertung', (
            ('id', orm['sasse.Bewertung:id']),
            ('teilnehmer', orm['sasse.Bewertung:teilnehmer']),
            ('posten', orm['sasse.Bewertung:posten']),
            ('bewertungsart', orm['sasse.Bewertung:bewertungsart']),
            ('wert', orm['sasse.Bewertung:wert']),
        ))
        db.send_create_signal('sasse', ['Bewertung'])
        
        # Adding model 'Teilnehmer'
        db.create_table('sasse_teilnehmer', (
            ('id', orm['sasse.Teilnehmer:id']),
            ('disziplin', orm['sasse.Teilnehmer:disziplin']),
            ('startnummer', orm['sasse.Teilnehmer:startnummer']),
            ('disqualifiziert', orm['sasse.Teilnehmer:disqualifiziert']),
            ('ausgeschieden', orm['sasse.Teilnehmer:ausgeschieden']),
        ))
        db.send_create_signal('sasse', ['Teilnehmer'])
        
        # Adding model 'Schiffeinzel'
        db.create_table('sasse_schiffeinzel', (
            ('teilnehmer_ptr', orm['sasse.Schiffeinzel:teilnehmer_ptr']),
            ('steuermann', orm['sasse.Schiffeinzel:steuermann']),
            ('vorderfahrer', orm['sasse.Schiffeinzel:vorderfahrer']),
            ('sektion', orm['sasse.Schiffeinzel:sektion']),
            ('kategorie', orm['sasse.Schiffeinzel:kategorie']),
            ('schiffsart', orm['sasse.Schiffeinzel:schiffsart']),
        ))
        db.send_create_signal('sasse', ['Schiffeinzel'])
        
        # Adding model 'Postenart'
        db.create_table('sasse_postenart', (
            ('id', orm['sasse.Postenart:id']),
            ('name', orm['sasse.Postenart:name']),
        ))
        db.send_create_signal('sasse', ['Postenart'])
        
        # Adding model 'Kategorie'
        db.create_table('sasse_kategorie', (
            ('id', orm['sasse.Kategorie:id']),
            ('disziplinart', orm['sasse.Kategorie:disziplinart']),
            ('name', orm['sasse.Kategorie:name']),
            ('alter_von', orm['sasse.Kategorie:alter_von']),
            ('alter_bis', orm['sasse.Kategorie:alter_bis']),
            ('geschlecht', orm['sasse.Kategorie:geschlecht']),
        ))
        db.send_create_signal('sasse', ['Kategorie'])
        
        # Adding model 'Disziplinart'
        db.create_table('sasse_disziplinart', (
            ('id', orm['sasse.Disziplinart:id']),
            ('name', orm['sasse.Disziplinart:name']),
        ))
        db.send_create_signal('sasse', ['Disziplinart'])
        
        # Adding model 'Schiffsektion'
        db.create_table('sasse_schiffsektion', (
            ('teilnehmer_ptr', orm['sasse.Schiffsektion:teilnehmer_ptr']),
            ('gruppe', orm['sasse.Schiffsektion:gruppe']),
            ('position', orm['sasse.Schiffsektion:position']),
            ('schiffsart', orm['sasse.Schiffsektion:schiffsart']),
        ))
        db.send_create_signal('sasse', ['Schiffsektion'])
        
        # Adding model 'Person'
        db.create_table('sasse_person', (
            ('teilnehmer_ptr', orm['sasse.Person:teilnehmer_ptr']),
            ('mitglied', orm['sasse.Person:mitglied']),
            ('sektion', orm['sasse.Person:sektion']),
            ('kategorie', orm['sasse.Person:kategorie']),
        ))
        db.send_create_signal('sasse', ['Person'])
        
        # Adding model 'Gruppe'
        db.create_table('sasse_gruppe', (
            ('teilnehmer_ptr', orm['sasse.Gruppe:teilnehmer_ptr']),
            ('chef', orm['sasse.Gruppe:chef']),
            ('sektion', orm['sasse.Gruppe:sektion']),
            ('name', orm['sasse.Gruppe:name']),
        ))
        db.send_create_signal('sasse', ['Gruppe'])
        
        # Adding model 'Kranzlimite'
        db.create_table('sasse_kranzlimite', (
            ('id', orm['sasse.Kranzlimite:id']),
            ('disziplin', orm['sasse.Kranzlimite:disziplin']),
            ('kategorie', orm['sasse.Kranzlimite:kategorie']),
            ('wert', orm['sasse.Kranzlimite:wert']),
        ))
        db.send_create_signal('sasse', ['Kranzlimite'])
        
        # Adding model 'Bewertungsart'
        db.create_table('sasse_bewertungsart', (
            ('id', orm['sasse.Bewertungsart:id']),
            ('name', orm['sasse.Bewertungsart:name']),
            ('signum', orm['sasse.Bewertungsart:signum']),
            ('einheit', orm['sasse.Bewertungsart:einheit']),
            ('wertebereich', orm['sasse.Bewertungsart:wertebereich']),
            ('defaultwert', orm['sasse.Bewertungsart:defaultwert']),
            ('reihenfolge', orm['sasse.Bewertungsart:reihenfolge']),
            ('postenart', orm['sasse.Bewertungsart:postenart']),
        ))
        db.send_create_signal('sasse', ['Bewertungsart'])
        
        # Adding ManyToManyField 'Postenart.disziplinarten'
        db.create_table('sasse_postenart_disziplinarten', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('postenart', models.ForeignKey(orm.Postenart, null=False)),
            ('disziplinart', models.ForeignKey(orm.Disziplinart, null=False))
        ))
        
        # Adding ManyToManyField 'Disziplin.kategorien'
        db.create_table('sasse_disziplin_kategorien', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('disziplin', models.ForeignKey(orm.Disziplin, null=False)),
            ('kategorie', models.ForeignKey(orm.Kategorie, null=False))
        ))
        
        # Creating unique_together for [wettkampf, name] on Disziplin.
        db.create_unique('sasse_disziplin', ['wettkampf_id', 'name'])
        
        # Creating unique_together for [disziplin, name] on Posten.
        db.create_unique('sasse_posten', ['disziplin_id', 'name'])
        
        # Creating unique_together for [teilnehmer, posten, bewertungsart] on Bewertung.
        db.create_unique('sasse_bewertung', ['teilnehmer_id', 'posten_id', 'bewertungsart_id'])
        
        # Creating unique_together for [gruppe, position] on Schiffsektion.
        db.create_unique('sasse_schiffsektion', ['gruppe_id', 'position'])
        
        # Creating unique_together for [disziplin, startnummer] on Teilnehmer.
        db.create_unique('sasse_teilnehmer', ['disziplin_id', 'startnummer'])
        
    
    
    def backwards(self, orm):
        
        # Deleting unique_together for [disziplin, startnummer] on Teilnehmer.
        db.delete_unique('sasse_teilnehmer', ['disziplin_id', 'startnummer'])
        
        # Deleting unique_together for [gruppe, position] on Schiffsektion.
        db.delete_unique('sasse_schiffsektion', ['gruppe_id', 'position'])
        
        # Deleting unique_together for [teilnehmer, posten, bewertungsart] on Bewertung.
        db.delete_unique('sasse_bewertung', ['teilnehmer_id', 'posten_id', 'bewertungsart_id'])
        
        # Deleting unique_together for [disziplin, name] on Posten.
        db.delete_unique('sasse_posten', ['disziplin_id', 'name'])
        
        # Deleting unique_together for [wettkampf, name] on Disziplin.
        db.delete_unique('sasse_disziplin', ['wettkampf_id', 'name'])
        
        # Deleting model 'Sektion'
        db.delete_table('sasse_sektion')
        
        # Deleting model 'Posten'
        db.delete_table('sasse_posten')
        
        # Deleting model 'Wettkampf'
        db.delete_table('sasse_wettkampf')
        
        # Deleting model 'Richtzeit'
        db.delete_table('sasse_richtzeit')
        
        # Deleting model 'Mitglied'
        db.delete_table('sasse_mitglied')
        
        # Deleting model 'Disziplin'
        db.delete_table('sasse_disziplin')
        
        # Deleting model 'Bewertung'
        db.delete_table('sasse_bewertung')
        
        # Deleting model 'Teilnehmer'
        db.delete_table('sasse_teilnehmer')
        
        # Deleting model 'Schiffeinzel'
        db.delete_table('sasse_schiffeinzel')
        
        # Deleting model 'Postenart'
        db.delete_table('sasse_postenart')
        
        # Deleting model 'Kategorie'
        db.delete_table('sasse_kategorie')
        
        # Deleting model 'Disziplinart'
        db.delete_table('sasse_disziplinart')
        
        # Deleting model 'Schiffsektion'
        db.delete_table('sasse_schiffsektion')
        
        # Deleting model 'Person'
        db.delete_table('sasse_person')
        
        # Deleting model 'Gruppe'
        db.delete_table('sasse_gruppe')
        
        # Deleting model 'Kranzlimite'
        db.delete_table('sasse_kranzlimite')
        
        # Deleting model 'Bewertungsart'
        db.delete_table('sasse_bewertungsart')
        
        # Dropping ManyToManyField 'Postenart.disziplinarten'
        db.delete_table('sasse_postenart_disziplinarten')
        
        # Dropping ManyToManyField 'Disziplin.kategorien'
        db.delete_table('sasse_disziplin_kategorien')
        
    
    
    models = {
        'sasse.bewertung': {
            'Meta': {'unique_together': "(('teilnehmer', 'posten', 'bewertungsart'),)"},
            'bewertungsart': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Bewertungsart']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'posten': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Posten']"}),
            'teilnehmer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sasse.Teilnehmer']"}),
            'wert': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'})
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
