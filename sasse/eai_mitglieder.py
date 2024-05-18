# -*- coding: utf-8 -*-

import sys
import openpyxl

from sasse.models import Mitglied, Sektion

def iter_excel_openpyxl(worksheet):
    rows = worksheet.rows
    headers = [str(cell.value) for cell in next(rows)]
    for row in rows:
        yield dict(zip(headers, (cell.value for cell in row)))

def map_geschlecht(satAdminValue):
    if satAdminValue == 'Weiblich':
        return 'f'
    else:
        return 'm'

sektion_cache = {}
for sektion in Sektion.objects.filter():
    sektion_cache[sektion.nummer] = sektion

# Erzeuge Objekt mit geparsten Werten
def parse_row(row):
    m = Mitglied()
    m.nummer = row['Personennummer']
    m.name = row['Nachname']
    m.vorname = row['Vorname']
    m.geburtsdatum = row['Geburtsdatum'].date()
    m.geschlecht = map_geschlecht(row['Geschlecht'])
    m.sektion = sektion_cache[row['Vereinsnummer']]
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
    with open(filename, 'rb') as f:
        workbook = openpyxl.load_workbook(f, read_only=True)
        worksheet = workbook.active
        unchanged = 0
        changed = 0
        nummer_changed = 0
        inserted = 0
        sys.stdout.write("Importiere Mitgliederdaten")
        for i, row in enumerate(iter_excel_openpyxl(worksheet)):
            from_input = parse_row(row)
            try:
                m = Mitglied.objects.get(nummer=from_input.nummer)
            except Mitglied.DoesNotExist:
                existing_mitglieder = []
                for mitglied in Mitglied.objects.filter(
                        sektion=from_input.sektion,
                        name=from_input.name,
                        vorname=from_input.vorname,
                        geburtsdatum__year=from_input.geburtsdatum.year,
                        geschlecht=from_input.geschlecht
                        ):
                    existing_mitglieder.append(mitglied)
                if len(existing_mitglieder) == 0:
                    # Neues Mitglied
                    m = Mitglied(nummer=from_input.nummer)
                elif len(existing_mitglieder) == 1:
                    m = existing_mitglieder[0]
                    msg = "\nUpdate Nummer von %s auf %s für %s" % (m.nummer, from_input.nummer, m)
                    sys.stdout.write(msg)
                    nummer_changed += 1
                else:
                    # Nehme den ersten Duplicate für den Nummer update
                    m = existing_mitglieder[0]
                    numbers = []
                    for n in existing_mitglieder:
                        numbers.append(n.nummer)
                    sys.stdout.write("\nWARN: %s existiert mehrfach: %s" % (from_input, numbers))
                    nummer_changed += 1
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
        sys.stdout.write("\nfertig.")
        sys.stdout.write("\nChanged: %d (davon mit Nummer: %d), Inserted: %d, Unchanged: %d\n" % (
               changed, nummer_changed, inserted, unchanged))
