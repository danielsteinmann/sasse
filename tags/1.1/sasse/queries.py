# -*- coding: utf-8 -*-

from decimal import Decimal
from itertools import groupby
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
        dict['note'] = new_bew(row[i], PUNKT); i += 1
        dict['richtzeit'] = new_bew(row[i], ZEIT); i += 1
        yield dict

def read_notenliste(disziplin, posten, sektion=None, startnummern=[]):
    sql = render_to_string('notenliste.sql',
            {"posten": posten, "sektion": sektion, "startnummern": startnummern})
    args = [disziplin.id]
    if sektion:
        args.append(sektion.id)
    if startnummern:
        args += startnummern
        placeholder = '%s'
        placeholders = ', '.join(placeholder for unused in startnummern)
        sql = sql.replace("__startnummern__", placeholders)
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
    sql = render_to_string('rangliste.sql', {"disziplin": disziplin, "kategorie": kategorie})
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
        dict['ausgeschieden'] = row[i]; i+=1
        dict['disqualifiziert'] = row[i]; i+=1
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
        if dict['ausgeschieden']:
            dict['rang'] = 'AUSG'
        elif dict['disqualifiziert']:
            dict['rang'] = 'DISQ'
        elif dict['doppelstarter'] and not doppelstarter_mit_rang:
            dict['rang'] = 'DS'
        else:
            dict['rang'] = rang
            if (punkt_tot_prev, zeit_tot_prev) != (dict['punkt_tot'].note, dict['zeit_tot'].zeit):
                rang += 1
            punkt_tot_prev = dict['punkt_tot'].note
            zeit_tot_prev = dict['zeit_tot'].zeit
        yield dict

def sort_rangliste(dict):
    if dict['ausgeschieden'] or dict['disqualifiziert']:
        return 99
    if dict['kranz'] and not dict['doppelstarter']:
        return 1
    if dict['kranz'] and dict['doppelstarter']:
        return 2
    if not dict['kranz'] and not dict['doppelstarter']:
        return 3
    if not dict['kranz'] and dict['doppelstarter']:
        return 5
    return 6

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
    punkte_sum = 0
    for row in cursor:
        dict = {}; i = 0
        dict['posten'] = row[i]; i += 1
        dict['posten_art'] = row[i]; i += 1
        dict['abzug'] = new_bew(row[i], PUNKT); i += 1
        dict['note'] = new_bew(row[i], PUNKT); i += 1
        dict['richtzeit'] = new_bew(row[i], ZEIT); i += 1
        dict['zeit'] = new_bew(row[i], ZEIT); i += 1
        dict['punkte'] = new_bew(row[i], PUNKT); i += 1
        zeit_sum += dict['zeit'].zeit
        punkte_sum += dict['punkte'].note
        if dict['posten_art'] == 'Zeitnote':
            dict['abzug'] = ""
            dict['note'] = ""
        else:
            dict['zeit'] = ""
        yield dict
    dict = {}
    dict['zeit'] = new_bew(zeit_sum, ZEIT)
    dict['punkte'] = new_bew(punkte_sum, PUNKT)
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
    sql = render_to_string('kranzlimite.sql', {"disziplin": disziplin, "kategorie": None})
    args = [disziplin.id, disziplin.id, disziplin.disziplinart_id]
    cursor = connection.cursor()
    cursor.execute(sql, args)
    wettkaempfer_sum = 0
    wettkaempfer_mit_kranz_sum = 0
    schiffe_sum = 0
    schiffe_mit_kranz_sum = 0
    for row in cursor:
        dict = {}; i = 0
        dict['kategorie'] = row[i]; i += 1
        dict['limite_in_punkte'] = row[i]; i += 1
        dict['wettkaempfer'] = row[i]; i += 1
        dict['wettkaempfer_ueber_limite'] = row[i]; i += 1
        dict['wettkaempfer_mit_kranz_in_prozent'] = (
                round((dict['wettkaempfer_ueber_limite']*Decimal("1.0")
                 / dict['wettkaempfer']) * Decimal("100"), 1))
        wettkaempfer_sum += dict['wettkaempfer']
        wettkaempfer_mit_kranz_sum += dict['wettkaempfer_ueber_limite']
        dict['schiffe'] = row[i]; i += 1
        dict['schiffe_ueber_limite'] = row[i]; i += 1
        dict['schiffe_ueber_limite_in_prozent'] = (
                round((dict['schiffe_ueber_limite']*Decimal("1.0")
                 / dict['schiffe']) * Decimal("100"), 1))
        schiffe_sum += dict['schiffe']
        schiffe_mit_kranz_sum += dict['schiffe_ueber_limite']
        yield dict
    dict = {}
    dict['wettkaempfer'] = wettkaempfer_sum
    dict['wettkaempfer_ueber_limite'] = wettkaempfer_mit_kranz_sum
    dict['schiffe'] = schiffe_sum
    dict['schiffe_ueber_limite'] = schiffe_mit_kranz_sum
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
    select count(t.id)
      from (
         select schiff.steuermann_id as id
           from sasse_teilnehmer tn
           join sasse_schiffeinzel schiff on (schiff.teilnehmer_ptr_id = tn.id)
          where tn.disziplin_id = %s
            and schiff.kategorie_id = %s
         union
         select schiff.vorderfahrer_id as id
           from sasse_teilnehmer tn
           join sasse_schiffeinzel schiff on (schiff.teilnehmer_ptr_id = tn.id)
          where tn.disziplin_id = %s
            and schiff.kategorie_id = %s
      ) as t
    """
    args = [disziplin.id, kategorie.id, disziplin.id, kategorie.id]
    cursor.execute(sql, args)
    row = cursor.fetchone()
    return row[0]

def create_mitglieder_nummer():
    cursor = connection.cursor()
    sql = "select max(nummer) from sasse_mitglied where nummer >= '99000'"
    cursor.execute(sql)
    row = cursor.fetchone()
    nummer = row[0]
    if not nummer:
        nummer = u"99000"
    else:
        nummer = u"%d" % (int(nummer)+1,)
    return unicode(nummer)

def sind_doppelstarter(wettkampf, disziplinart, steuermann, vorderfahrer):
    """
    Aus Performance Gründen in *einem* SQL Select für beide den Test machen
    """
    cursor = connection.cursor()
    sql = """
 select m.id, count(tn.id) as anzahl_starts
   from sasse_mitglied m
   join sasse_schiffeinzel schiff on schiff.vorderfahrer_id = m.id or schiff.steuermann_id = m.id
   join sasse_teilnehmer tn on tn.id = schiff.teilnehmer_ptr_id
   join sasse_disziplin dz on dz.id = tn.disziplin_id
  where dz.wettkampf_id = %s
    and dz.disziplinart_id = %s
    and m.id in (%s, %s)
  group by m.id
 having count(tn.id) > 0
     """
    args = [wettkampf.id, disziplinart.id, steuermann.id, vorderfahrer.id]
    cursor.execute(sql, args)
    hinten_ds = False
    vorne_ds = False
    for row in cursor:
        mitglied_id = row[0]
        anzahl_starts = row[1]
        if mitglied_id == steuermann.id:
            hinten_ds = True
        else:
            vorne_ds = True
    return (hinten_ds, vorne_ds)

def read_doppelstarter(wettkampf, disziplinart):
    ds = _read_doppelstarter(wettkampf, disziplinart)
    grouped_ds = _group_doppelstarter(ds)
    sorted_ds = sorted(grouped_ds, key=_sort_doppelstarter_nummer)
    _mark_double_trouble(sorted_ds)
    return sorted_ds

def _read_doppelstarter(wettkampf, disziplinart):
    cursor = connection.cursor()
    sql = """
select m.id
     , m.name
     , m.vorname
     , s.name as sektion
     , tn.startnummer
     , dz.name as disziplin
     , case when schiff.steuermann_ist_ds or schiff.vorderfahrer_ist_ds then 1 else 0 end as ds
  from (
        -- Markiert (Steuermann)
        select schiff.steuermann_id as id
          from sasse_disziplin dz
          join sasse_teilnehmer tn on (tn.disziplin_id = dz.id)
          join sasse_schiffeinzel schiff on (schiff.teilnehmer_ptr_id = tn.id)
         where dz.wettkampf_id = %s
           and dz.disziplinart_id = %s
           and schiff.steuermann_ist_ds
        union
        -- Markiert (Vorderfahrer)
        select schiff.vorderfahrer_id as id
          from sasse_disziplin dz
          join sasse_teilnehmer tn on (tn.disziplin_id = dz.id)
          join sasse_schiffeinzel schiff on (schiff.teilnehmer_ptr_id = tn.id)
         where dz.wettkampf_id = %s
           and dz.disziplinart_id = %s
           and schiff.vorderfahrer_ist_ds
        union
        -- Berechnet
        select m.id
          from sasse_mitglied m
          join sasse_sektion s on (s.id = m.sektion_id)
          join sasse_schiffeinzel schiff on schiff.vorderfahrer_id = m.id or schiff.steuermann_id = m.id
          join sasse_teilnehmer tn on tn.id = schiff.teilnehmer_ptr_id
          join sasse_disziplin dz on dz.id = tn.disziplin_id
         where dz.wettkampf_id = %s
           and dz.disziplinart_id = %s
         group by m.id, m.name, m.vorname, s.name
        having count(tn.id) > 1
        ) as ds
   join sasse_mitglied m on (m.id = ds.id)
   join sasse_sektion s on (s.id = m.sektion_id)
   join sasse_schiffeinzel schiff on schiff.vorderfahrer_id = ds.id or schiff.steuermann_id = ds.id
   join sasse_teilnehmer tn on tn.id = schiff.teilnehmer_ptr_id
   join sasse_disziplin dz on dz.id = tn.disziplin_id
  where dz.wettkampf_id = %s
    and dz.disziplinart_id = %s
  -- Muss nach Mitglied sortieren, damit in Python 'groupby' moeglich ist.
  order by m.name, m.vorname, s.name, ds, tn.startnummer
     """
    args = [wettkampf.id, disziplinart.id, wettkampf.id, disziplinart.id, wettkampf.id, disziplinart.id, wettkampf.id, disziplinart.id]
    cursor.execute(sql, args)
    for row in cursor:
        result = {}; i = 0
        result['mid'] = row[i]; i += 1
        result['name'] = row[i]; i += 1
        result['vorname'] = row[i]; i += 1
        result['sektion'] = row[i]; i += 1
        result['startnummer'] = row[i]; i += 1
        result['disziplin'] = row[i]; i += 1
        result['doppelstarter'] = row[i]; i += 1
        yield result

def _group_doppelstarter(doppelstarter):
    result = []
    for key, group in groupby(doppelstarter, lambda x: (x['name'], x['vorname'],x['sektion'])):
        row = {}
        row['name'] = key[0]
        row['vorname'] = key[1]
        row['sektion'] = key[2]
        row['trouble'] = False
        normal = []
        doppel = []
        for item in group:
            if item['doppelstarter']:
                doppel.append(item)
            else:
                normal.append(item)
        row['doppel'] = doppel
        row['normal'] = normal
        if len(normal) != 1 or len(doppel) != 1:
            row['trouble'] = True
        result.append(row)
    return result

def _sort_doppelstarter_nummer(row):
    doppel = row['doppel']
    if doppel:
        return doppel[0]['startnummer']
    else:
        # Passiert durch Falscheingabe, wenn ein Mitglied mehrfach startet,
        # aber nicht als Doppelstarter markiert ist.
        return None

def _mark_double_trouble(sorted_ds):
    """
    Am Fällbaumcup 2011 kam es vor, dass zwei Doppelstarter zusammen in einem
    Schiff auf der Rangliste erschienen. Dieser Zustand wird hier geprüft.
    """
    previous_row = None
    for row in sorted_ds:
        if previous_row and previous_row['doppel'] and row['doppel']:
            previous_item = previous_row['doppel'][0]
            item = row['doppel'][0]
            if item['startnummer'] == previous_item['startnummer']:
                previous_row['trouble'] = True
                row['trouble'] = True
        previous_row = row

