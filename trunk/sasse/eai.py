import sys
from datetime import date
import xlrd
from sasse.models import Mitglied

def parse_row(sh, i):
    sektion_id_str = "%02d" % int(sh.cell_value(i, 0))
    nummer = sektion_id_str + "%03d" % int(sh.cell_value(i, 1))
    name = sh.cell_value(i, 2)
    vorname = sh.cell_value(i, 3)
    gebdatum = xlrd.xldate_as_tuple(sh.cell_value(i, 4), 0)
    geschlecht_str = sh.cell_value(i, 5)
    geschlecht = 'm'
    if geschlecht_str == 'w':
        geschlecht = 'f'
    # Erzeuge Objekt mit geparsten Werten
    m = Mitglied()
    m.nummer = nummer
    m.sektion_id = int(sektion_id_str)
    m.name = name
    m.vorname = vorname
    m.geburtsdatum = date(gebdatum[0],gebdatum[1],gebdatum[2])
    m.geschlecht = geschlecht
    return m

def update(mitglied, from_input):
    changed = False
    if from_input.nummer != mitglied.nummer:
        mitglied.nummer = from_input.nummer
        changed = True
    if from_input.sektion_id != mitglied.sektion_id:
        mitglied.sektion_id = from_input.sektion_id
        changed = True
    if from_input.name != mitglied.name:
        mitglied.name = from_input.name
        changed = True
    if from_input.vorname != mitglied.vorname:
        mitglied.vorname = from_input.vorname
        changed = True
    if from_input.geburtsdatum != mitglied.geburtsdatum:
        mitglied.geburtsdatum = from_input.geburtsdatum
        changed = True
    if from_input.geschlecht != mitglied.geschlecht:
        mitglied.geschlecht = from_input.geschlecht
        changed = True
    return changed

def handle_file_upload(filename):
    wb = xlrd.open_workbook(filename)
    sh = wb.sheet_by_index(0)
    unchanged = 0
    changed = 0
    nummer_changed = 0
    inserted = 0
    sys.stdout.write("Importiere Mitgliederdaten")
    for i in range(sh.nrows):
        if i == 0:
            continue
        from_input = parse_row(sh, i)
        try:
            m = Mitglied.objects.get(nummer=from_input.nummer)
        except Mitglied.DoesNotExist:
            count = 0
            for mitglied in Mitglied.objects.filter(
                    sektion__id=from_input.sektion_id,
                    name=from_input.name,
                    vorname=from_input.vorname,
                    geburtsdatum__year=from_input.geburtsdatum.year,
                    geschlecht=from_input.geschlecht
                    ):
                count += 1
                if count == 1:
                    m = mitglied
                    # Mitglied nummer change from %s to %s" % (m.nummer, from_input.nummer)
                    nummer_changed += 1
                else:
                    sys.stdout.write("\n%s %s (%s): Existiert mehr als einmal (%s) " % (mitglied.name, mitglied.vorname, mitglied.nummer, m.nummer))
            if count == 0:
                # New Mitglied
                m = Mitglied(nummer=from_input.nummer)
        updated = update(m, from_input)
        if not updated:
            unchanged += 1
        elif m.id:
            m.save()
            changed += 1
        else:
            m.save()
            inserted += 1
        # Show prgress
        if i % 100 == 0:
            sys.stdout.write(".")
            sys.stdout.flush()
    sys.stdout.write("fertig.\n")
    sys.stdout.write("Changed: %d/%d, Inserted: %d, Unchanged: %d\n" % (
           changed, nummer_changed, inserted, unchanged))
