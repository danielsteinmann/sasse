# -*- coding: utf-8 -*-

from datetime import datetime

from reportlab.platypus import Paragraph, TableStyle
from reportlab.platypus import Table as Platypus_Table
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

PAGE_WIDTH, PAGE_HEIGHT = A4

def create_rangliste_pdf(rangliste):
    result = []
    rows = []
    rows.append(['Rang', 'Steuermann', 'Vorderfahrer', 'Sektion', 'Zeit', 'Punkte'])
    ohne_kranz = 0
    for r in rangliste:
        rang = r['rang']
        if r['doppelstarter']: rang = 'DS'
        record = (rang, r['steuermann'], r['vorderfahrer'], r['sektion'], r['zeit_tot'], r['punkt_tot'])
        rows.append(record)
        if not r['kranz']: ohne_kranz += 1
    col_widths = (30, 100, 100, 100, 50, 40)
    table_props = [
        ('LINEBELOW', (0,0), (-1,0), 1, colors.black),
        ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 8),
        ('FONT', (0,1), (-1,-1), 'Helvetica', 8),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('ALIGN', (1,0), (3,-1), 'LEFT'),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('ALIGN', (-2,0), (-1,-1), 'CENTER'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), (None, colors.HexColor(0xf0f0f0))),
        ]
    if ohne_kranz:
        kranzlimite_row = len(rows) - ohne_kranz
        #rows.insert(kranzlimite_row, [Paragraph('Kranzlimite', ParagraphStyle(name='Normal'))])
        rows.insert(kranzlimite_row, ['Kranzlimite'])
        table_props.extend([
            ('SPAN', (0,kranzlimite_row), (-1,kranzlimite_row)),
            ('BOX', (0,kranzlimite_row), (-1,kranzlimite_row), 1, colors.grey),
            ])
    table_style = TableStyle(table_props)
    result.append(Platypus_Table(rows, repeatRows=1, colWidths=col_widths, style=table_style))
    return result

def rangliste_header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 12)
    canvas.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT-1*cm, "Rangliste %s, Kat. %s, %s %d" % (
        doc.disziplin.disziplinart, doc.kategorie.name, doc.wettkampf.name, doc.wettkampf.jahr()))
    canvas.setFont('Helvetica', 8)
    current_datetime = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    canvas.drawString(2*cm, 1*cm, "%s" % (current_datetime,))
    canvas.drawRightString(PAGE_WIDTH-2*cm/2.0, 1*cm, "Seite %d" % (doc.page,))
    canvas.restoreState()
