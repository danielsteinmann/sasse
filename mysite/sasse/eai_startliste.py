# -*- coding: utf-8 -*-
"""
Read-Only, eventuell Caching
- Wettkampf
- Disziplin
- Sektion
- Kategorie

Read-Write
- Schiffeinzel
- Mitglied
"""

import datetime
import csv
from django.forms.models import model_to_dict
from sasse.models import *

import warnings
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.core.cache import CacheKeyWarning
warnings.simplefilter("ignore", CacheKeyWarning)


COLUMNS = (
        "WETTKAMPF_JAHR",
        "WETTKAMPF_NAME",
        "DISZIPLIN_NAME",
        "STARTNUMMER",
        "DISQUALIFIZIERT",
        "AUSGESCHIEDEN",
        "SEKTION_NAME",
        "KATEGORIE_NAME",
        "STEUERMANN_IST_DS",
        "VORDERFAHRER_IST_DS",
        "STEUERMANN_NUMMER",
        "STEUERMANN_NAME",
        "STEUERMANN_VORNAME",
        "STEUERMANN_GEBURTSDATUM",
        "STEUERMANN_GESCHLECHT",
        "STEUERMANN_SEKTION_NAME",
        "VORDERFAHRER_NUMMER",
        "VORDERFAHRER_NAME",
        "VORDERFAHRER_VORNAME",
        "VORDERFAHRER_GEBURTSDATUM",
        "VORDERFAHRER_GESCHLECHT",
        "VORDERFAHRER_SEKTION_NAME",
        )

def serialize_schiffeinzel(schiff):
    row = {
        "WETTKAMPF_JAHR": schiff.disziplin.wettkampf.jahr(),
        "WETTKAMPF_NAME": schiff.disziplin.wettkampf.name.encode("utf-8"),
        "DISZIPLIN_NAME": schiff.disziplin.name.encode("utf-8"),
        "STARTNUMMER": schiff.startnummer,
        "DISQUALIFIZIERT": str(schiff.disqualifiziert),
        "AUSGESCHIEDEN": str(schiff.ausgeschieden),
        "SEKTION_NAME": schiff.sektion.name.encode("utf-8"),
        "KATEGORIE_NAME": schiff.kategorie.name.encode("utf-8"),
        "STEUERMANN_IST_DS": str(schiff.steuermann_ist_ds),
        "VORDERFAHRER_IST_DS": str(schiff.vorderfahrer_ist_ds),
        "STEUERMANN_NUMMER": schiff.steuermann.nummer,
        "STEUERMANN_NAME": schiff.steuermann.name.encode("utf-8"),
        "STEUERMANN_VORNAME": schiff.steuermann.vorname.encode("utf-8"),
        "STEUERMANN_GEBURTSDATUM": str(schiff.steuermann.geburtsdatum),
        "STEUERMANN_GESCHLECHT": schiff.steuermann.geschlecht,
        "STEUERMANN_SEKTION_NAME": schiff.steuermann.sektion.name.encode("utf-8"),
        "VORDERFAHRER_NUMMER": schiff.vorderfahrer.nummer,
        "VORDERFAHRER_NAME": schiff.vorderfahrer.name.encode("utf-8"),
        "VORDERFAHRER_VORNAME": schiff.vorderfahrer.vorname.encode("utf-8"),
        "VORDERFAHRER_GEBURTSDATUM": str(schiff.vorderfahrer.geburtsdatum),
        "VORDERFAHRER_GESCHLECHT": schiff.vorderfahrer.geschlecht,
        "VORDERFAHRER_SEKTION_NAME": schiff.vorderfahrer.sektion.name.encode("utf-8"),
        }
    return row

def deserialize_schiffeinzel(wettkampf, row):
    jahr = int(row['WETTKAMPF_JAHR'])
    wname = str(row['WETTKAMPF_NAME'], 'utf-8')
    dname = str(row['DISZIPLIN_NAME'], 'utf-8')
    if wettkampf.name != wname or wettkampf.jahr() != jahr:
        raise StartlisteImportException("Eingelesene Startliste ist nicht für den aktuellen Wettkampf")
    disziplin = get_disziplin(jahr, wname, dname)
    sektion = get_sektion(str(row["SEKTION_NAME"], 'utf-8'))
    kategorie = get_kategorie(disziplin, str(row["KATEGORIE_NAME"], 'utf-8'))
    steuermann = cru_mitglied("STEUERMANN", row)
    vorderfahrer = cru_mitglied("VORDERFAHRER", row)
    schiff = Schiffeinzel(
            disziplin=disziplin,
            startnummer=int(row['STARTNUMMER']),
            disqualifiziert=str2bool(row["DISQUALIFIZIERT"]),
            ausgeschieden=str2bool(row["AUSGESCHIEDEN"]),
            steuermann=steuermann,
            vorderfahrer=vorderfahrer,
            steuermann_ist_ds=str2bool(row["STEUERMANN_IST_DS"]),
            vorderfahrer_ist_ds=str2bool(row["VORDERFAHRER_IST_DS"]),
            sektion=sektion,
            kategorie=kategorie,
            )
    return schiff

def deserialize_mitglied(prefix, row):
    sektion_str = str(row[prefix + "_SEKTION_NAME"], 'utf-8')
    sektion = get_sektion(sektion_str)
    geburtsdatum_str = row[prefix + "_GEBURTSDATUM"]
    geburtsdatum = datetime.datetime.strptime(geburtsdatum_str, "%Y-%m-%d").date()
    mitglied = Mitglied(
            nummer=row[prefix + "_NUMMER"],
            name=str(row[prefix + "_NAME"], 'utf-8'),
            vorname=str(row[prefix + "_VORNAME"], 'utf-8'),
            geschlecht=row[prefix + "_GESCHLECHT"],
            geburtsdatum=geburtsdatum,
            sektion=sektion,
            )
    return mitglied

class StartlisteImportException(Exception):
    pass

def str2bool(v):
  return v.lower() in ("ja", "yes", "true", "t", "1")

def get_disziplin(wettkampf_jahr, wettkampf_name, disziplin_name):
    key = dict(
            name=disziplin_name,
            wettkampf__name=wettkampf_name,
            wettkampf__von__year=wettkampf_jahr,
            )
    result = cache.get(key)
    if result:
        return result
    try:
        result = Disziplin.objects.select_related().get(**key)
        cache.set(key, result, 10)
        return result
    except Disziplin.DoesNotExist:
        msg = "%s/%s: Wettkampf/Disziplin nicht gefunden." % (wettkampf_name, disziplin_name)
        raise ObjectDoesNotExist(msg)

def get_sektion(sektion_name):
    key = dict(name=sektion_name)
    result = cache.get(key)
    if result:
        return result
    try:
        result = Sektion.objects.get(**key)
        cache.set(key, result, 10)
        return result
    except Sektion.DoesNotExist:
        msg = "%s: Keine solche Sektion gefunden." % sektion_name
        raise ObjectDoesNotExist(msg)

def get_kategorie(disziplin, kategorie_name):
    key = dict(
            disziplinart=disziplin.disziplinart,
            name=kategorie_name,
            )
    result = cache.get(key)
    if result:
        return result
    try:
        result = Kategorie.objects.get(**key)
        cache.set(key, result, 10)
        return result
    except Kategorie.DoesNotExist:
        msg = "%s: Keine solche Kategorie gefunden." % kategorie_name
        raise ObjectDoesNotExist(msg)

def gleiche_instanz(a, b):
    a_dict = model_to_dict(a)
    b_dict = model_to_dict(b)
    del a_dict['id']
    del b_dict['id']
    if a_dict.get('teilnehmer_ptr'):
        del a_dict['teilnehmer_ptr']
        del b_dict['teilnehmer_ptr']
    result = a_dict == b_dict
    return result

def cru_mitglied(prefix, row):
    from_input = deserialize_mitglied(prefix, row)
    try:
        from_db = Mitglied.objects.get(nummer=from_input.nummer)
    except Mitglied.DoesNotExist:
        from_input.save(force_insert=True)
        return from_input
    else:
        if gleiche_instanz(from_db, from_input):
            return from_db
        else:
            from_input.id = from_db.id
            from_input.save(force_update=True)
            return from_input

def cru_schiffeinzel(wettkampf, row):
    from_input = deserialize_schiffeinzel(wettkampf, row)
    try:
        from_db = Schiffeinzel.objects.get(
                disziplin=from_input.disziplin,
                startnummer=from_input.startnummer,
                )
    except Schiffeinzel.DoesNotExist:
        from_input.save(force_insert=True)
        result = (from_input, "insert")
    else:
        if gleiche_instanz(from_db, from_input):
            result = (from_db, "unchanged")
        else:
            from_input.id = from_db.id
            from_input.save(force_update=True)
            result = (from_input, "update")
    return result

def load(wettkampf, csvfile):
    reader = csv.DictReader(csvfile)
    stats = {'insert': 0, 'update': 0, 'unchanged': 0}
    for row in reader:
        try:
            obj, mode = cru_schiffeinzel(wettkampf, row)
            stats[mode] += 1
        except ObjectDoesNotExist as e:
            msg = 'Zeile %d: %s' % (reader.line_num, e)
            raise StartlisteImportException(msg)
    return stats

def dump(wettkampf, csvfile):
    writer = csv.DictWriter(csvfile, COLUMNS)
    writer.writeheader()
    for schiff in Schiffeinzel.objects.select_related().filter(
            disziplin__wettkampf=wettkampf,
            disziplin__disziplinart__name="Einzelfahren",
            ).order_by('disziplin__name', 'startnummer'):
        row = serialize_schiffeinzel(schiff)
        writer.writerow(row)
