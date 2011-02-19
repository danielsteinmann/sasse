# -*- coding: utf-8 -*-

from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import BaseDocTemplate
from reportlab.platypus import PageBreak
from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer
from reportlab.platypus import TableStyle
from reportlab.platypus import Table as Platypus_Table
from reportlab.platypus.doctemplate import PageTemplate
from reportlab.platypus.flowables import DocExec
from reportlab.platypus.frames import Frame

PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT = ParagraphStyle('left', fontName='Helvetica', fontSize=8, alignment=TA_LEFT)
CENTER = ParagraphStyle('center', parent=LEFT, alignment=TA_CENTER)
RIGHT = ParagraphStyle('right', parent=LEFT, alignment=TA_RIGHT)
DS_MARKER = '<font size=-2> (DS)</font>'

def _extract_jahrgang(geburtstag):
    return ' <font size=-2>' + geburtstag.strftime('%Y') + "</font>"

def create_rangliste_doctemplate(wettkampf, disziplin):
    f = Frame(1*cm, 1*cm, PAGE_WIDTH-2*cm, PAGE_HEIGHT-2.5*cm, id='normal')
    pt = PageTemplate(id="Rangliste", frames=f, onPageEnd=write_rangliste_header_footer)
    doc = BaseDocTemplate(None, pageTemplates=[pt], pagesize=A4)
    doc.wettkampf = wettkampf
    doc.disziplin = disziplin
    return doc

def create_rangliste_flowables(rangliste, kategorie, kranzlimite):
    result = []
    data = [['Rang', 'Steuermann', 'Vorderfahrer', 'Sektion', 'Stnr', 'Zeit', 'Punkte']]
    col_widths = (30, 140, 140, 80, 30, 40, 30)
    anzahl_ohne_kranz = 0
    for row in rangliste:
        if not row['kranz']: anzahl_ohne_kranz += 1
        if row['doppelstarter']: row['rang'] = 'DS'
        if row['steuermann_ist_ds']: row['steuermann'] += DS_MARKER
        if row['vorderfahrer_ist_ds']: row['vorderfahrer'] += DS_MARKER
        row['steuermann'] += _extract_jahrgang(row['steuermann_jg'])
        row['vorderfahrer'] += _extract_jahrgang(row['vorderfahrer_jg'])
        record = []
        record.append(Paragraph(unicode(row['rang']), CENTER))
        record.append(Paragraph(row['steuermann'], LEFT))
        record.append(Paragraph(row['vorderfahrer'], LEFT))
        record.append(Paragraph(row['sektion'], LEFT))
        record.append(Paragraph(unicode(row['startnummer']), CENTER))
        record.append(Paragraph(unicode(row['zeit_tot']), CENTER))
        record.append(Paragraph(unicode(row['punkt_tot']), CENTER))
        data.append(record)
    table_props = [
        ('LINEBELOW', (0,0), (-1,0), 1, colors.black),
        ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 8),
        ('FONT', (0,1), (-1,-1), 'Helvetica', 8),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('ALIGN', (1,0), (3,-1), 'LEFT'),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('ALIGN', (-2,0), (-1,-1), 'CENTER'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), (None, colors.HexColor(0xf0f0f0))),
        ]
    if anzahl_ohne_kranz:
        kranzlimite_row = len(data) - anzahl_ohne_kranz
        data.insert(kranzlimite_row, [Paragraph('Kranzlimite: %s Punkte' % (kranzlimite), LEFT)])
        table_props.extend([
            ('SPAN', (0,kranzlimite_row), (-1,kranzlimite_row)),
            ('BACKGROUND', (0,kranzlimite_row), (-1,kranzlimite_row), colors.lightgrey),
            ])
    result.append(DocExec("kategorie_name = '%s'" % kategorie.name))
    result.append(Platypus_Table(data, repeatRows=1, colWidths=col_widths, style=TableStyle(table_props)))
    result.append(PageBreak())
    return result

def write_rangliste_header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.drawString(2*cm, PAGE_HEIGHT-1*cm, "Rangliste %s" % (doc.disziplin.disziplinart))
    canvas.setFont('Helvetica', 14)
    canvas.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT-1*cm, "Kategorie %s" % (doc.docEval("kategorie_name")))
    canvas.setFont('Helvetica', 8)
    canvas.drawRightString(PAGE_WIDTH-2*cm, PAGE_HEIGHT-1*cm, "%s %d" % (doc.wettkampf.name, doc.wettkampf.jahr()))
    canvas.setFont('Helvetica', 8)
    #current_datetime = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    #canvas.drawString(2*cm, 1*cm, "%s" % (current_datetime,))
    canvas.drawCentredString(PAGE_WIDTH/2, 1*cm, "Seite %d" % (doc.page,))
    canvas.restoreState()


#
# Notenblatt
#

def create_notenblatt_doctemplate(wettkampf, disziplin):
    f = Frame(2.5*cm, 1*cm, PAGE_WIDTH-2*cm, PAGE_HEIGHT-2.5*cm, id='normal')
    pt = PageTemplate(id="Notenblatt", frames=f)
    doc = BaseDocTemplate(None, pageTemplates=[pt], pagesize=A4)
    return doc

def create_notenblatt_flowables(posten_werte, schiffeinzel):
    result = []
    data = [
            ["Startnummer:", unicode(schiffeinzel.startnummer)],
            ["Kategorie:", schiffeinzel.kategorie],
            ["Sektion:", schiffeinzel.sektion],
            ["Steuermann:", "%s %s" % (schiffeinzel.steuermann.name, schiffeinzel.steuermann.vorname)],
            ["Vorderfahrer:", "%s %s" % (schiffeinzel.vorderfahrer.name, schiffeinzel.vorderfahrer.vorname)],
            ]
    col_widths = (70, 100)
    table_props = [
        ('FONT', (0,0), (0,-1), 'Helvetica-Bold', 8),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ]
    result.append(Platypus_Table(data, hAlign="LEFT", colWidths=col_widths, style=TableStyle(table_props)))
    result.append(Spacer(1, 30))
    header = []
    header.append(Paragraph('<strong>Posten</strong>', CENTER))
    header.append(Paragraph('<strong>Übungsteil</strong>', LEFT))
    header.append(Paragraph('<strong>Abzug</strong>', RIGHT))
    header.append(Paragraph('<strong>Note</strong>', RIGHT))
    header.append(Paragraph('<strong>Zeit</strong>', CENTER))
    header.append(Paragraph('<strong>Total</strong>', RIGHT))
    data = []
    data.append(header)
    col_widths = (40, 200, 30, 30, 40, 30)
    for row in posten_werte:
        record = []
        if row.get('posten'):
            record.append(Paragraph(row['posten'], CENTER))
            record.append(Paragraph(row['posten_art'], LEFT))
            record.append(Paragraph(unicode(row['abzug']), RIGHT))
            record.append(Paragraph(unicode(row['note']), RIGHT))
            record.append(Paragraph(unicode(row['zeit']), CENTER))
            record.append(Paragraph(unicode(row['total']), RIGHT))
        else:
            record.append("")
            record.append("")
            record.append("")
            record.append("")
            record.append(Paragraph("<strong>" + unicode(row['zeit']) + "</strong>", CENTER))
            record.append(Paragraph("<strong>" + unicode(row['total']) + "</strong>", RIGHT))
        data.append(record)
    table_props = [
        ('LINEBELOW', (0,0), (-1,0), 1, colors.black),
        ('LINEABOVE', (0,-1), (-1,-1), 1, colors.black),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), (None, colors.HexColor(0xf0f0f0))),
        ]
    result.append(Platypus_Table(data, hAlign="LEFT", colWidths=col_widths, style=TableStyle(table_props)))
    return result

