from datetime import date
import xlrd
from sasse.models import Mitglied
from sasse.models import Sektion

wb = xlrd.open_workbook("20091013-Mitgliederdaten.xls")
sh = wb.sheet_by_index(0)

for i in range(sh.nrows):
    if i == 0:
        continue
    sektion_str = "" + sh.cell_value(i, 1)
    nummer = sektion_str + sh.cell_value(i, 2)
    name = sh.cell_value(i, 3)
    vorname = sh.cell_value(i, 4)
    gebdatum = xlrd.xldate_as_tuple(sh.cell_value(i, 5), 0)
    geschlecht_str = sh.cell_value(i, 6)
    geschlecht = 'm'
    if geschlecht_str == 'w':
        geschlecht = 'f'
    try:
        m = Mitglied.objects.get(nummer=nummer)
    except Mitglied.DoesNotExist:
        print "Neues Mitglied %s" % nummer
        m = Mitglied(nummer=nummer)
    m.sektion=Sektion.objects.get(id=int(sektion_str))
    m.name=name
    m.vorname=vorname
    m.geburtsdatum=date(gebdatum[0],gebdatum[1],gebdatum[2])
    m.geschlecht=geschlecht
    m.save()
