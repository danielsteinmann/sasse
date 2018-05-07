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
from models import Gruppe
from models import SektionsfahrenKranzlimiten

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

def read_beste_fahrerpaare(disziplin, kategorie_namen=['C', 'D'], anzahl_schiffe=6):
    cursor = connection.cursor()
    sql = """
with topn as (
   select sektion.name as Sektion
        , tn.startnummer as Startnummer
        , max(hinten.name || ' / ' || vorne.name) as Fahrerpaar
        , max(kat.name) as Kategorie
        , sum(b.zeit) as Zeit
        , sum(b.note) as Punkte
        , count(tn.startnummer) over (partition by sektion.name) anz
        , row_number() over (partition by sektion.name
                                 order by sum(b.note) desc) as rk
     from sasse_teilnehmer tn
     join sasse_schiffeinzel schiff on (schiff.teilnehmer_ptr_id = tn.id)
     join bewertung_calc b on (b.teilnehmer_id = tn.id)
     join sasse_kategorie kat on (kat.id = schiff.kategorie_id)
     join sasse_sektion sektion on (sektion.id = schiff.sektion_id)
     join sasse_mitglied vorne on (vorne.id = schiff.vorderfahrer_id)
     join sasse_mitglied hinten on (hinten.id = schiff.steuermann_id)
    where tn.disziplin_id = %(disziplin_id)s
      and kat.name in (%(kategorien)s)
      and not tn.ausgeschieden and not tn.disqualifiziert
      and not schiff.steuermann_ist_ds and not schiff.vorderfahrer_ist_ds
    group by tn.startnummer, sektion.name
    )
select topn.sektion
     , topn.startnummer
     , topn.fahrerpaar
     , topn.kategorie
     , topn.punkte
     , sum(topn.punkte) over (partition by topn.sektion) as total
  from topn
 where topn.rk <= %(anzahl)d
   and topn.anz >= %(anzahl)d
 order by total desc, topn.sektion, topn.rk
     """ % {
             'disziplin_id': disziplin.id,
             'kategorien': ",".join([ "'%s'" % k for k in kategorie_namen]),
             'anzahl': anzahl_schiffe}
    cursor.execute(sql)
    for row in cursor:
        yield {
                'sektion': row[0],
                'startnummer': row[1],
                'fahrerpaar': row[2],
                'kategorie': row[3],
                'punkte': row[4],
                'total': row[5],
                }

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

def read_sektionsfahren_gruppen_counts(disziplin, gruppe=None):
    cursor = connection.cursor()
    sql = render_to_string('sektionsfahren_gruppe_counts.sql',
            {"disziplin": disziplin, "gruppe": gruppe})
    args = [disziplin.id]
    if gruppe:
        args.append(gruppe.id)
    cursor.execute(sql, args)
    anz_schiffe = {}
    anz_jps = {}
    anz_frauen = {}
    anz_senioren = {}
    for row in cursor.fetchall():
        grp = row[0]
        anz_schiffe[grp] = row[1]
        anz_jps[grp] = row[2]
        anz_frauen[grp] = row[3]
        anz_senioren[grp] = row[4]
    return (anz_schiffe, anz_jps, anz_frauen, anz_senioren)

def read_sektionsfahren_gruppe_punkte(disziplin):
    sql = """
select grp.name as Gruppe
     , sum(b.note) as Punkte
  from sasse_schiffsektion schiff
  join sasse_teilnehmer tn on (tn.id = schiff.teilnehmer_ptr_id)
  join sasse_gruppe grp on (grp.teilnehmer_ptr_id = schiff.gruppe_id)
  join bewertung_calc b on (b.teilnehmer_id = tn.id)
 where 1=1
   and tn.disziplin_id = %s
 group by grp.name
    """
    args = [disziplin.id]
    cursor = connection.cursor()
    cursor.execute(sql, args)
    punkte = {}
    for row in cursor:
        grp = row[0]
        punkte[grp] = Decimal(str(row[1]))
    return punkte

def read_sektionsfahren_rangliste_gruppe(disziplin):
    punkte = read_sektionsfahren_gruppe_punkte(disziplin)
    result = []
    for g in Gruppe.objects.with_counts(disziplin):
        if g.anz_schiffe() > 0:
            g.gefahren = (punkte[g.name] / g.anz_schiffe()).quantize(Decimal("0.001"))
            g.zuschlag = (((g.anz_jps() + g.anz_frauen() + g.anz_senioren()) * Decimal("2")) / g.anz_schiffe()).quantize(Decimal("0.001"))
            g.total = g.gefahren + g.zuschlag - g.abzug_gruppe
            g.gewichtet = g.total * g.anz_schiffe()
            result.append(g)
    result.sort(key=lambda g: (-g.total, -g.anz_schiffe()))
    rang = 1
    for g in result:
        g.rang = rang
        rang += 1
    return result

def read_sektionsfahren_rangliste(disziplin):
    result = []
    limiten, created = SektionsfahrenKranzlimiten.objects.get_or_create(disziplin=disziplin)
    ausser_konkurrenz = None
    ausser_konkurrenz_name = None
    if limiten.ausser_konkurrenz:
        ausser_konkurrenz_name = limiten.ausser_konkurrenz.name
    gruppen_rangliste = read_sektionsfahren_rangliste_gruppe(disziplin)
    gruppen_rangliste.sort(key=lambda g: (g.sektion.name, g.name))
    for sektion, gruppen in groupby(gruppen_rangliste, lambda g: g.sektion.name):
        anz_gruppen = 0
        anz_schiffe = 0
        anz_jps = 0
        anz_frauen = 0
        anz_senioren = 0
        abzug_sektion = 0
        gewichtet = 0
        gruppen = list(gruppen)
        for g in gruppen:
            anz_gruppen += 1
            anz_schiffe += g.anz_schiffe()
            anz_jps += g.anz_jps()
            anz_frauen += g.anz_frauen()
            anz_senioren += g.anz_senioren()
            abzug_sektion += g.abzug_sektion
            gewichtet += g.gewichtet
        gewichtet_avg = (gewichtet / anz_schiffe).quantize(Decimal("0.001"))
        row = {
            'name': sektion,
            'gruppen': gruppen,
            'anz_gruppen': anz_gruppen,
            'anz_schiffe': anz_schiffe,
            'anz_jps': anz_jps,
            'anz_frauen': anz_frauen,
            'anz_senioren': anz_senioren,
            'abzug': abzug_sektion,
            'gewichtet': gewichtet,
            'gewichtet_avg': gewichtet_avg,
            'total': gewichtet_avg - abzug_sektion,
            }
        if sektion != ausser_konkurrenz_name:
            result.append(row)
        else:
            ausser_konkurrenz = row
    result.sort(key=lambda s: (-s['total'], -s['anz_schiffe']))
    rang = 1
    for s in result:
        s['rang'] = rang
        total = s['total']
        if total >= limiten.gold:
            kranz_typ = 'Gold'
        elif total >= limiten.silber:
            kranz_typ = 'Silber'
        else:
            kranz_typ = 'Lorbeer'
        s['kranz_typ'] = kranz_typ
        rang += 1
    if ausser_konkurrenz is not None:
        ausser_konkurrenz['rang'] = "AC"
        ausser_konkurrenz['kranz_typ'] = ''
        result.insert(0, ausser_konkurrenz)
    return result

def sort_sektionsfahren_rangliste(disziplin, rangliste):
    limiten, created = SektionsfahrenKranzlimiten.objects.get_or_create(disziplin=disziplin)

def read_sektionsfahren_notenblatt_gruppe(gruppe):
    sql = """
select grp.name as "Gruppe"
     , p.name as "Posten"
     , pa.name as "Postenart"
     , sum(case when schiff.position = 1 then b.note end) as "1"
     , sum(case when schiff.position = 2 then b.note end) as "2"
     , sum(case when schiff.position = 3 then b.note end) as "3"
     , sum(case when schiff.position = 4 then b.note end) as "4"
     , sum(case when schiff.position = 5 then b.note end) as "5"
  from sasse_teilnehmer tn
  join sasse_schiffsektion schiff on (schiff.teilnehmer_ptr_id = tn.id)
  join sasse_gruppe grp on (grp.teilnehmer_ptr_id = schiff.gruppe_id)
  join bewertung_calc b on (b.teilnehmer_id = tn.id)
  join sasse_posten p on (p.id = b.posten_id)
  join sasse_postenart pa on (pa.id = p.postenart_id)
 where schiff.gruppe_id = %s
 group by grp.name, p.name, pa.name, p.reihenfolge
 order by grp.name, p.reihenfolge
    """
    args = [gruppe.id]
    cursor = connection.cursor()
    cursor.execute(sql, args)
    schiff_1_sum = 0
    schiff_2_sum = 0
    schiff_3_sum = 0
    schiff_4_sum = 0
    schiff_5_sum = 0
    for row in cursor:
        result = {}; i = 0
        result['gruppe'] = row[i]; i += 1
        result['posten'] = row[i]; i += 1
        result['postenart'] = row[i]; i += 1
        result['schiff_1'] = new_bew(row[i], PUNKT); i += 1
        result['schiff_2'] = new_bew(row[i], PUNKT); i += 1
        result['schiff_3'] = new_bew(row[i], PUNKT); i += 1
        result['schiff_4'] = new_bew(row[i], PUNKT); i += 1
        result['schiff_5'] = new_bew(row[i], PUNKT); i += 1
        schiff_1_sum += result['schiff_1'].note
        schiff_2_sum += result['schiff_2'].note
        schiff_3_sum += result['schiff_3'].note
        schiff_4_sum += result['schiff_4'].note
        schiff_5_sum += result['schiff_5'].note
        yield result
    yield {
            'schiff_1': schiff_1_sum,
            'schiff_2': schiff_2_sum,
            'schiff_3': schiff_3_sum,
            'schiff_4': schiff_4_sum,
            'schiff_5': schiff_5_sum,
            }

def read_sektionsfahren_rangliste_schiff(disziplin):
    sql = """
select grp.name as gruppe
     , schiff.position as schiff
     , max(s1.name) ft1_steuermann
     , max(s2.name) ft2_steuermann
     , max(v1.name) ft1_vorderfahrer
     , max(v2.name) ft2_vorderfahrer
     , sum(b.zeit) as zeit
     , sum(b.note) as punkte
  from sasse_schiffsektion schiff
  join sasse_teilnehmer tn on (tn.id = schiff.teilnehmer_ptr_id)
  join sasse_gruppe grp on (grp.teilnehmer_ptr_id = schiff.gruppe_id)
  join bewertung_calc b on (b.teilnehmer_id = tn.id)
  join sasse_mitglied s1 on (s1.id = schiff.ft1_steuermann_id)
  join sasse_mitglied s2 on (s2.id = schiff.ft2_steuermann_id)
  join sasse_mitglied v1 on (v1.id = schiff.ft1_vorderfahrer_id)
  join sasse_mitglied v2 on (v2.id = schiff.ft2_vorderfahrer_id)
 where 1=1
   and tn.disziplin_id = %s
 group by grp.name, schiff.position
 order by punkte desc, zeit asc
    """
    args = [disziplin.id]
    cursor = connection.cursor()
    cursor.execute(sql, args)
    for i, row in enumerate(cursor, 1):
        result = {}
        result['rang'] = i
        result['gruppe'] = row[0]
        result['schiff'] = row[1]
        result['ft1_steuermann'] = row[2]
        result['ft2_steuermann'] = row[3]
        result['ft1_vorderfahrer'] = row[4]
        result['ft2_vorderfahrer'] = row[5]
        result['zeit'] = new_bew(row[6], ZEIT)
        result['note'] = new_bew(row[7], PUNKT)
        yield result

def read_sektionsfahren_topzeiten(posten, topn=15):
    sql = """
select grp.name as gruppe
     , schiff.position as schiff
     , s1.name ft1_steuermann
     , s2.name ft2_steuermann
     , v1.name  ft1_vorderfahrer
     , v2.name  ft2_vorderfahrer
     , b.zeit as Zeit
     , b.note as Note
     , b.richtzeit as Richtzeit
     , zi.startnummer_calc as startnummer_calc
  from sasse_schiffsektion schiff
  join sasse_teilnehmer tn on (tn.id = schiff.teilnehmer_ptr_id)
  join sasse_gruppe grp on (grp.teilnehmer_ptr_id = schiff.gruppe_id)
  join bewertung_calc b on (b.teilnehmer_id = tn.id)
  join sasse_mitglied s1 on (s1.id = schiff.ft1_steuermann_id)
  join sasse_mitglied s2 on (s2.id = schiff.ft2_steuermann_id)
  join sasse_mitglied v1 on (v1.id = schiff.ft1_vorderfahrer_id)
  join sasse_mitglied v2 on (v2.id = schiff.ft2_vorderfahrer_id)
  left outer join sasse_sektionsfahrenzeitimport zi on (zi.schiffsektion_id = tn.id and zi.posten_id = b.posten_id)
 where 1=1
   and b.posten_id = %s
   and b.zeit > 0
 order by Zeit asc
    """
    args = [posten.id]
    cursor = connection.cursor()
    cursor.execute(sql, args)
    for n, row in enumerate(cursor):
        if n == topn:
            break
        result = {}; i = 0
        result['gruppe'] = row[i]; i += 1
        result['schiff'] = row[i]; i += 1
        result['ft1_steuermann'] = row[i]; i += 1
        result['ft2_steuermann'] = row[i]; i += 1
        result['ft1_vorderfahrer'] = row[i]; i += 1
        result['ft2_vorderfahrer'] = row[i]; i += 1
        result['zeit'] = new_bew(row[i], ZEIT); i += 1
        result['note'] = new_bew(row[i], PUNKT); i += 1
        result['richtzeit'] = new_bew(row[i], ZEIT); i += 1
        result['startnummer_calc'] = row[i]; i += 1
        yield result

def read_schwimmen_gestartete_kategorien(disziplin):
    cursor = connection.cursor()
    sql = """
    select kat.name
      from sasse_kategorie kat
     where kat.name in (
            select distinct sw.kategorie
              from sasse_teilnehmer tn
              join sasse_schwimmer sw on (sw.teilnehmer_ptr_id = tn.id)
             where tn.disziplin_id = %s
           )
     order by kat.reihenfolge
    """
    args = [disziplin.id]
    cursor.execute(sql, args)
    for row in cursor:
        yield row[0]

def read_einzelschnueren_gestartete_kategorien(disziplin):
    cursor = connection.cursor()
    sql = """
    select kat.name
      from sasse_kategorie kat
     where kat.name in (
            select distinct sw.kategorie
              from sasse_teilnehmer tn
              join sasse_einzelschnuerer sw on (sw.teilnehmer_ptr_id = tn.id)
             where tn.disziplin_id = %s
           )
     order by kat.reihenfolge
    """
    args = [disziplin.id]
    cursor.execute(sql, args)
    for row in cursor:
        yield row[0]

def read_gruppenschnueren_gestartete_kategorien(disziplin):
    def sort_by_kategorie_name(kategorie_name):
        if kategorie_name == 'JP':
            return 1
        else:
            return 2
    cursor = connection.cursor()
    sql = """
    select distinct kategorie
      from sasse_teilnehmer tn
      join sasse_schnuergruppe sw on (sw.teilnehmer_ptr_id = tn.id)
     where tn.disziplin_id = %s
    """
    args = [disziplin.id]
    cursor.execute(sql, args)
    kategories = []
    for row in cursor:
        kategories.append(row[0])
    return sorted(kategories, key=sort_by_kategorie_name)

def read_bootfaehrenbau_gestartete_kategorien(disziplin):
    cursor = connection.cursor()
    sql = """
    select distinct kategorie
      from sasse_teilnehmer tn
      join sasse_bootfaehrengruppe sw on (sw.teilnehmer_ptr_id = tn.id)
     where tn.disziplin_id = %s
    """
    args = [disziplin.id]
    cursor.execute(sql, args)
    for row in cursor:
        yield row[0]

def read_einzelfahren_null_zeiten(disziplin):
    sql = """
select p.name as posten
     , tn.startnummer as startnummer
     , sektion.name as sektion
     , hinten.name as steuermann
     , vorne.name as vorderfahrer
  from sasse_teilnehmer tn
  join sasse_schiffeinzel schiff on (schiff.teilnehmer_ptr_id = tn.id)
  join bewertung_calc b on (b.teilnehmer_id = tn.id)
  join sasse_kategorie kat on (kat.id = schiff.kategorie_id)
  join sasse_sektion sektion on (sektion.id = schiff.sektion_id)
  join sasse_mitglied vorne on (vorne.id = schiff.vorderfahrer_id)
  join sasse_mitglied hinten on (hinten.id = schiff.steuermann_id)
  join sasse_disziplin d on (d.id = tn.disziplin_id)
  join sasse_posten p on (p.id = b.posten_id)
 where tn.disziplin_id = %s
   and b.zeit is null
   and b.note is null
   and b.bewertungsart_id = 16  -- Zeit
   and not tn.ausgeschieden and not tn.disqualifiziert
 order by p.name, tn.startnummer
    """
    args = [disziplin.id]
    cursor = connection.cursor()
    cursor.execute(sql, args)
    for row in cursor:
        result = {}
        result['posten'] = row[0]
        result['startnummer'] = row[1]
        result['sektion'] = row[2]
        result['steuermann'] = row[3]
        result['vorderfahrer'] = row[4]
        yield result

def read_sektionsfahren_null_zeiten(disziplin):
    sql = """
select p.name as posten
     , grp.name as gruppe
     , schiff.position as schiff
  from sasse_schiffsektion schiff
  join sasse_teilnehmer tn on (tn.id = schiff.teilnehmer_ptr_id)
  join sasse_gruppe grp on (grp.teilnehmer_ptr_id = schiff.gruppe_id)
  join bewertung_calc b on (b.teilnehmer_id = tn.id)
  join sasse_posten p on (p.id = b.posten_id)
 where 1=1
   and tn.disziplin_id = %s
   and b.zeit is null
   and b.note is null
   and b.bewertungsart_id = 16  -- Zeit
   and not tn.ausgeschieden and not tn.disqualifiziert
 order by p.name, tn.startnummer
    """
    args = [disziplin.id]
    cursor = connection.cursor()
    cursor.execute(sql, args)
    for row in cursor:
        result = {}; i = 0
        result['posten'] = row[i]; i += 1
        result['gruppe'] = row[i]; i += 1
        result['schiff'] = row[i]; i += 1
        yield result

