# -*- coding: utf-8 -*-

from datetime import datetime

from reportlab.platypus import Paragraph, TableStyle
from reportlab.platypus import BaseDocTemplate
from reportlab.platypus import Table as Platypus_Table
from reportlab.platypus import PageBreak
from reportlab.platypus.doctemplate import PageTemplate
from reportlab.platypus.flowables import DocExec
from reportlab.platypus.frames import Frame
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

PAGE_WIDTH, PAGE_HEIGHT = A4

def create_rangliste_doctemplate(wettkampf, disziplin):
    f = Frame(1*cm, 1*cm, PAGE_WIDTH-2*cm, PAGE_HEIGHT-2.5*cm, id='normal')
    pt = PageTemplate(id="Rangliste", frames=f, onPageEnd=write_rangliste_header_footer)
    doc = BaseDocTemplate(None, pageTemplates=[pt], pagesize=A4)
    doc.wettkampf = wettkampf
    doc.disziplin = disziplin
    return doc

def create_rangliste_flowables(rangliste, kategorie):
    result = []
    data = []
    styles = getSampleStyleSheet()
    data.append(['Rang', 'Steuermann', 'Vorderfahrer', 'Sektion', 'Zeit', 'Punkte'])
    anzahl_ohne_kranz = 0
    ps_left = ParagraphStyle('left', fontName='Helvetica', fontSize=8, alignemt=0)
    ps_center = ParagraphStyle('center', parent=ps_left, alignment=1)
    for row in rangliste:
        if not row['kranz']: anzahl_ohne_kranz += 1
        if row['doppelstarter']: row['rang'] = 'DS'
        if row['steuermann_ist_ds']: row['steuermann'] += ' (DS)'
        if row['vorderfahrer_ist_ds']: row['vorderfahrer'] += ' (DS)'
        record = []
        record.append(Paragraph(unicode(row['rang']), ps_center))
        record.append(Paragraph(row['steuermann'], ps_left))
        record.append(Paragraph(row['vorderfahrer'], ps_left))
        record.append(Paragraph(row['sektion'], ps_left))
        record.append(Paragraph(unicode(row['zeit_tot']), ps_center))
        record.append(Paragraph(unicode(row['punkt_tot']), ps_center))
        data.append(record)
    col_widths = (30, 120, 120, 80, 50, 30)
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
        data.insert(kranzlimite_row, [Paragraph('Kranzlimite', ps_left)])
        table_props.extend([
            ('SPAN', (0,kranzlimite_row), (-1,kranzlimite_row)),
            ('BACKGROUND', (0,kranzlimite_row), (-1,kranzlimite_row), colors.lightgrey),
            ])
    result.append(DocExec("kategorie_name = '%s'" % kategorie.name))
    table_style = TableStyle(table_props)
    result.append(Platypus_Table(data, repeatRows=1, colWidths=col_widths, style=table_style))
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
