from datetime import date
import xlrd
from sasse.models import Mitglied

def parse_row(sh, i):
    sektion_id_str = "" + sh.cell_value(i, 1)
    nummer = sektion_id_str + sh.cell_value(i, 2)
    name = sh.cell_value(i, 3)
    vorname = sh.cell_value(i, 4)
    gebdatum = xlrd.xldate_as_tuple(sh.cell_value(i, 5), 0)
    geschlecht_str = sh.cell_value(i, 6)
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

def handle_file_upload(file_content):
    wb = xlrd.open_workbook(file_contents=file_content)
    sh = wb.sheet_by_index(0)
    changed = 0
    inserted = 0
    for i in range(sh.nrows):
        if i == 0:
            continue
        from_input = parse_row(sh, i)
        try:
            m = Mitglied.objects.get(nummer=from_input.nummer)
        except Mitglied.DoesNotExist:
            m = Mitglied(nummer=from_input.nummer)
        if update(m, from_input):
            if m.id:
                changed += 1
                print "Mitglied change: %s" % m.nummer
            else:
                inserted += 1
                print "Mitglied neu   : %s" % m.nummer
            m.save()
    print "Changed: %d, Inserted: %d" % (changed, inserted)


f = open("20091013-Mitgliederdaten.xls", 'r')
handle_file_upload(f.read())
f.close()
