# -*- coding: utf-8 -*-

from decimal import Decimal
from django.template.loader import render_to_string
from django.db import connection
from models import Bewertungsart
from models import Bewertung
from models import Schiffeinzel
from models import Kranzlimite
from models import Kategorie

# Hilfskonstanten
ZEIT = Bewertungsart(einheit='ZEIT')
PUNKT = Bewertungsart(einheit='PUNKT')

def new_bew(col, art):
    """
    Hilfsfunktion, damit ein Bewertung Objekt im Template einfach so verwendet
    werden kann, d.h. eine korrekte String Representation hat.
    """
    wert = Decimal()
    if col:
        wert = Decimal(str(col))
    if art.einheit == 'ZEIT':
        result = Bewertung(zeit=wert, bewertungsart=art)
    else:
        result = Bewertung(note=wert, bewertungsart=art)
    return result

def read_topzeiten(posten, topn=15):
    sql = render_to_string('topzeiten.sql')
    args = [posten.id]
    cursor = connection.cursor()
    cursor.execute(sql, args)
    for n, row in enumerate(cursor):
        if n == topn:
            break
        dict = {}; i = 0
        dict['startnummer'] = row[i]; i += 1
        dict['steuermann'] = row[i]; i += 1
        dict['vorderfahrer'] = row[i]; i += 1
        dict['sektion'] = row[i]; i += 1
        dict['kategorie'] = row[i]; i += 1
        dict['zeit'] = new_bew(row[i], ZEIT); i += 1
        dict['punkte'] = new_bew(row[i], PUNKT); i += 1
        dict['richtzeit'] = new_bew(row[i], ZEIT); i += 1
        yield dict

def read_notenliste(disziplin, posten, sektion=None):
    sql = render_to_string('notenliste.sql',
            {"posten": posten, "sektion": sektion})
    args = [disziplin.id]
    if sektion:
        args.append(sektion.id)
    cursor = connection.cursor()
    cursor.execute(sql, args)
    for row in cursor:
        dict = {}; i = 0
        dict['startnummer'] = row[i]; i += 1
        dict['steuermann'] = row[i]; i += 1
        dict['vorderfahrer'] = row[i]; i += 1
        dict['sektion'] = row[i]; i += 1
        dict['kategorie'] = row[i]; i += 1
        dict['zeit_tot'] = new_bew(row[i], ZEIT); i += 1
        dict['punkt_tot'] = new_bew(row[i], PUNKT); i += 1
        noten = []
        for p in posten:
            noten.append(new_bew(row[i], PUNKT)); i += 1
            if p.postenart.name == "Zeitnote":
                noten.append(new_bew(row[i], ZEIT)); i += 1
        dict['noten'] = noten
        yield dict

def read_rangliste(disziplin, kategorie, doppelstarter_mit_rang=False):
    sql = render_to_string('rangliste.sql')
    args = [disziplin.id, kategorie.id]
    cursor = connection.cursor()
    cursor.execute(sql, args)
    rang = 1
    punkt_tot_prev = None
    zeit_tot_prev = None
    for row in cursor:
        dict = {}; i = 0
        dict['rang'] = None
        dict['doppelstarter'] = False
        dict['startnummer'] = row[i]; i+=1
        dict['kranz'] = row[i]; i+=1
        dict['steuermann_ist_ds'] = row[i]; i+=1
        dict['vorderfahrer_ist_ds'] = row[i]; i+=1
        dict['steuermann'] = row[i]; i+=1
        dict['steuermann'] += ' ' + row[i]; i+=1
        dict['steuermann_jg'] = row[i]; i+=1
        dict['vorderfahrer'] = row[i]; i+=1
        dict['vorderfahrer'] += ' ' + row[i]; i+=1
        dict['vorderfahrer_jg'] = row[i]; i+=1
        dict['sektion'] = row[i]; i += 1
        dict['kategorie'] = row[i]; i += 1
        dict['zeit_tot'] = new_bew(row[i], ZEIT); i += 1
        dict['punkt_tot'] = new_bew(row[i], PUNKT); i += 1
        if dict['steuermann_ist_ds'] or dict['vorderfahrer_ist_ds']:
            dict['doppelstarter'] = True
        if (not dict['doppelstarter']) or doppelstarter_mit_rang:
            dict['rang'] = rang
            if (punkt_tot_prev, zeit_tot_prev) != (dict['punkt_tot'].note, dict['zeit_tot'].zeit):
                rang += 1
        punkt_tot_prev = dict['punkt_tot'].note
        zeit_tot_prev = dict['zeit_tot'].zeit
        yield dict

def sort_rangliste(dict):
    if dict['kranz'] and not dict['doppelstarter']:
        return 1
    if dict['kranz'] and dict['doppelstarter']:
        return 2
    if not dict['kranz'] and not dict['doppelstarter']:
        return 3
    if not dict['kranz'] and dict['doppelstarter']:
        return 4
    return 5

def read_notenblatt(disziplin, teilnehmer=None, sektion=None):
    sql = render_to_string('notenblatt.sql',
            {"teilnehmer": teilnehmer, "sektion": sektion})
    args = [disziplin.id]
    if teilnehmer:
        args.append(teilnehmer.id)
    if sektion:
        args.append(sektion.id)
    cursor = connection.cursor()
    cursor.execute(sql, args)
    zeit_sum = 0
    total_sum = 0
    for row in cursor:
        dict = {}; i = 0
        dict['posten'] = row[i]; i += 1
        dict['posten_art'] = row[i]; i += 1
        dict['abzug'] = new_bew(row[i], PUNKT); i += 1
        dict['note'] = new_bew(row[i], PUNKT); i += 1
        dict['zeit'] = new_bew(row[i], ZEIT); i += 1
        dict['total'] = new_bew(row[i], PUNKT); i += 1
        zeit_sum += dict['zeit'].zeit
        total_sum += dict['total'].note
        if dict['posten_art'] == 'Zeitnote':
            dict['abzug'] = ""
            dict['note'] = ""
        else:
            dict['zeit'] = ""
        yield dict
    dict = {}
    dict['zeit'] = new_bew(zeit_sum, ZEIT)
    dict['total'] = new_bew(total_sum, PUNKT)
    yield dict

def read_kranzlimite(disziplin, kategorie):
    result = None
    q = Kranzlimite.objects.filter(disziplin=disziplin, kategorie=kategorie)
    if q.count() > 0:
        result = q[0].wert
    return result

def read_kranzlimite_pro_kategorie(disziplin):
    limite_pro_kategorie = {}
    for kl in Kranzlimite.objects.filter(disziplin=disziplin):
        limite_pro_kategorie[kl.kategorie_id] = kl
    return limite_pro_kategorie

def read_kranzlimiten(disziplin):
    sql = render_to_string('kranzlimiten.sql', {"disziplin": disziplin})
    args = [disziplin.id]
    cursor = connection.cursor()
    cursor.execute(sql, args)
    wettkaempfer_sum = 0
    wettkaempfer_mit_kranz_sum = 0
    for row in cursor:
        dict = {}; i = 0
        dict['kategorie'] = row[i]; i += 1
        dict['limite_in_punkte'] = new_bew(row[i], PUNKT); i += 1
        dict['anzahl_raenge'] = row[i]; i += 1
        dict['anzahl_raenge_ueber_limite'] = row[i]; i += 1
        dict['doppelstarter'] = row[i]; i += 1
        dict['doppelstarter_ueber_limite'] = row[i]; i += 1
        # Kalkulationen
        dict['wettkaempfer'] = (
                2*dict['anzahl_raenge']
                - dict['doppelstarter'] )
        dict['wettkaempfer_ueber_limite'] = (
                2*dict['anzahl_raenge_ueber_limite']
                - dict['doppelstarter_ueber_limite'] )
        dict['wettkaempfer_mit_kranz_in_prozent'] = (
                round((dict['wettkaempfer_ueber_limite']*1.0
                 / dict['wettkaempfer']) * 100, 1))
        wettkaempfer_sum += dict['wettkaempfer']
        wettkaempfer_mit_kranz_sum += dict['wettkaempfer_ueber_limite']
        yield dict
    dict = {}
    dict['wettkaempfer'] = wettkaempfer_sum
    dict['wettkaempfer_ueber_limite'] = wettkaempfer_mit_kranz_sum
    yield dict

def read_startende_kategorien(disziplin):
    """
    Nur Kategorien, zu denen in denen auch tatsächlich Schiffe starten;
    deshalb geht disziplin.kategorien.all() nicht.
    """
    kategorien = Kategorie.objects.raw("""
        select kat.*
          from sasse_kategorie kat
         where kat.id in (
                select distinct schiff.kategorie_id
                  from sasse_schiffeinzel schiff
                  join sasse_teilnehmer tn on (tn.id = schiff.teilnehmer_ptr_id)
                 where tn.disziplin_id = %s
               )
         order by kat.reihenfolge
         """, [disziplin.id])
    return kategorien

def read_anzahl_wettkaempfer(disziplin, kategorie):
    cursor = connection.cursor()
    sql = """
    select count(id)
      from (
         select schiff.steuermann_id as id
           from sasse_teilnehmer tn on (tn.id = b.teilnehmer_id)
           join sasse_schiffeinzel schiff on (schiff.teilnehmer_ptr_id = tn.id)
          where tn.disziplin_id = %s
            and schiff.kategorie_id = %s
         union
         select schiff.vorderfahrer_id as id
           from sasse_teilnehmer tn on (tn.id = b.teilnehmer_id)
           join sasse_schiffeinzel schiff on (schiff.teilnehmer_ptr_id = tn.id)
          where tn.disziplin_id = %s
            and schiff.kategorie_id = %s
      )
    """
    args = [disziplin.id, kategorie.id, disziplin.id, kategorie.id]
    cursor.execute(sql, args)
    row = cursor.fetchone()
    return row[0]

def create_mitglieder_nummer():
    cursor = connection.cursor()
    sql = "select max(nummer)+1 from sasse_mitglied where nummer >= '99000'"
    cursor.execute(sql)
    row = cursor.fetchone()
    nummer = row[0]
    if not nummer:
        nummer = u"99000"
    return unicode(nummer)
