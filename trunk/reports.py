# -*- coding: utf-8 -*-

from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.styles import StyleSheet1
from reportlab.lib.units import cm
from reportlab.platypus import BaseDocTemplate
from reportlab.platypus import PageBreak
from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer
from reportlab.platypus import TableStyle
from reportlab.platypus import Table as Platypus_Table
from reportlab.platypus.doctemplate import PageTemplate
from reportlab.platypus.doctemplate import NextPageTemplate
from reportlab.platypus.flowables import DocExec
from reportlab.platypus.frames import Frame

PAGE_WIDTH, PAGE_HEIGHT = A4

def _create_style_sheet(baseFontSize=8):
    stylesheet = StyleSheet1()
    stylesheet.add(ParagraphStyle(name='left', fontName='Helvetica',
        fontSize=baseFontSize, alignment=TA_LEFT))
    stylesheet.add(ParagraphStyle('center', parent=stylesheet['left'], alignment=TA_CENTER))
    stylesheet.add(ParagraphStyle('right', parent=stylesheet['left'], alignment=TA_RIGHT))
    return stylesheet

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
    data = [['Rang', 'Steuermann', 'Vorderfahrer', 'Sektion', 'Stnr', 'Zeit', 'Punkte']]
    col_widths = (30, 140, 140, 80, 30, 40, 30)
    anzahl_ohne_kranz = 0
    ds_marker = '<font size=-2> (DS)</font>'
    ss = _create_style_sheet()
    for row in rangliste:
        if not row['kranz']: anzahl_ohne_kranz += 1
        if row['doppelstarter']: row['rang'] = 'DS'
        if row['steuermann_ist_ds']: row['steuermann'] += ds_marker
        if row['vorderfahrer_ist_ds']: row['vorderfahrer'] += ds_marker
        row['steuermann'] += _extract_jahrgang(row['steuermann_jg'])
        row['vorderfahrer'] += _extract_jahrgang(row['vorderfahrer_jg'])
        record = []
        record.append(Paragraph(unicode(row['rang']), ss['center']))
        record.append(Paragraph(row['steuermann'], ss['left']))
        record.append(Paragraph(row['vorderfahrer'], ss['left']))
        record.append(Paragraph(row['sektion'], ss['left']))
        record.append(Paragraph(unicode(row['startnummer']), ss['center']))
        record.append(Paragraph(unicode(row['zeit_tot']), ss['center']))
        record.append(Paragraph(unicode(row['punkt_tot']), ss['center']))
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
        text = Paragraph('Kranzlimite: %s Punkte' % (kranzlimite), ss['left'])
        data.insert(kranzlimite_row, [text, None, None, None, None, None, None])
        table_props.extend([
            ('SPAN', (0,kranzlimite_row), (-1,kranzlimite_row)),
            ('BACKGROUND', (0,kranzlimite_row), (-1,kranzlimite_row), colors.lightgrey),
            ])
    result = []
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
    f = Frame(2.5*cm, 1*cm, PAGE_WIDTH-2*cm, PAGE_HEIGHT-3*cm, id='normal')
    pt = PageTemplate(id="Notenblatt", frames=f, onPageEnd=write_notenblatt_header_footer)
    doc = BaseDocTemplate(None, pageTemplates=[pt], pagesize=A4)
    doc.wettkampf = wettkampf
    doc.disziplin = disziplin
    return doc

def write_notenblatt_header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica-Bold', 10)
    canvas.drawString(2.8*cm, PAGE_HEIGHT-1*cm, "Notenblatt %s" % (doc.disziplin.disziplinart))
    canvas.drawRightString(PAGE_WIDTH-2*cm, PAGE_HEIGHT-1*cm, "%s %d" % (doc.wettkampf.name, doc.wettkampf.jahr()))
    canvas.restoreState()

def create_notenblatt_flowables(posten_werte, schiffeinzel):
    result = []
    ss = _create_style_sheet(baseFontSize=10)
    # --------
    steuermann = schiffeinzel.steuermann
    vorderfahrer = schiffeinzel.vorderfahrer
    data = [
            ["Startnummer:", unicode(schiffeinzel.startnummer)],
            ["Steuermann:", "%s %s" % (steuermann.name, steuermann.vorname)],
            ["Vorderfahrer:", "%s %s" % (vorderfahrer.name, vorderfahrer.vorname)],
            ["Sektion:", schiffeinzel.sektion],
            ["Kategorie:", schiffeinzel.kategorie],
            ]
    col_widths = (70, 150)
    table_props = [
        ('FONT', (0,0), (-1,-1), 'Helvetica', 10),
        ('FONT', (1,0), (1,-1), 'Helvetica-Bold', 10),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ]
    result.append(DocExec("startnummer = '%d'" % schiffeinzel.startnummer))
    result.append(Platypus_Table(data, hAlign="LEFT", colWidths=col_widths, style=TableStyle(table_props)))
    result.append(Spacer(1, 30))
    # --------
    data = [['Posten', 'Übungsteil', 'Abzug', 'Note', 'Zeit', 'Total',]]
    col_widths = (40, 250, 40, 40, 55, 40)
    for row in posten_werte:
        record = []
        if row.get('posten'):
            record.append(Paragraph(row['posten'], ss['center']))
            record.append(Paragraph(row['posten_art'], ss['left']))
            record.append(unicode(row['abzug']))
            record.append(unicode(row['note']))
            record.append(unicode(row['zeit']))
            record.append(unicode(row['total']))
        else:
            for i in range(0,4): record.append("")
            record.append(unicode(row['zeit']))
            record.append(unicode(row['total']))
        data.append(record)
    table_props = [
        ('FONT', (0,0), (-1,-1), 'Helvetica', 10),
        ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 10),
        ('FONT', (0,-1), (-1,-1), 'Helvetica-Bold', 10),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('ALIGN', (-4,0), (-1,-1), 'RIGHT'),
        ('LINEBELOW', (0,0), (-1,0), 1, colors.black),
        ('LINEABOVE', (0,-1), (-1,-1), 1, colors.black),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), (None, colors.HexColor(0xf0f0f0))),
        ]
    result.append(Platypus_Table(data, hAlign="LEFT", colWidths=col_widths, style=TableStyle(table_props)))
    result.append(PageBreak())
    return result

#
# Startliste
#

def create_startliste_doctemplate(wettkampf, disziplin):
    f = Frame(1*cm, 1*cm, PAGE_WIDTH-2*cm, PAGE_HEIGHT-2.5*cm, id='normal')
    pt = PageTemplate(id="Startliste", frames=f, onPageEnd=write_startliste_header_footer)
    doc = BaseDocTemplate(None, pageTemplates=[pt], pagesize=A4)
    doc.wettkampf = wettkampf
    doc.disziplin = disziplin
    return doc

def write_startliste_header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica-Bold', 10)
    canvas.drawString(1.3*cm, PAGE_HEIGHT-1*cm, "Startliste %s" % (doc.disziplin.disziplinart))
    canvas.drawRightString(PAGE_WIDTH-1*cm, PAGE_HEIGHT-1*cm, "%s %d" % (doc.wettkampf.name, doc.wettkampf.jahr()))
    canvas.setFont('Helvetica', 8)
    canvas.drawCentredString(PAGE_WIDTH/2, 1*cm, "Seite %d" % (doc.page,))
    canvas.restoreState()

def create_startliste_flowables(schiffe):
    data = [['Stnr', 'Steuermann', 'Vorderfahrer', 'Kat', 'Sektion']]
    col_widths = (30, 180, 180, 25, 120)
    ss = _create_style_sheet(10)
    def mitglied_str(mitglied):
        return "%s %s<font size=-4> %s, %s, %s</font>" % (
                mitglied.name, mitglied.vorname,
                mitglied.nummer, mitglied.geburtsdatum.strftime('%Y'),
                mitglied.geschlecht)
    for s in schiffe:
        steuermann = s.steuermann
        vorderfahrer = s.vorderfahrer
        record = []
        record.append(Paragraph(unicode(s.startnummer), ss['center']))
        record.append(Paragraph(mitglied_str(steuermann), ss['left']))
        record.append(Paragraph(mitglied_str(vorderfahrer), ss['left']))
        record.append(Paragraph(s.kategorie.name, ss['center']))
        record.append(Paragraph(s.sektion.name, ss['left']))
        data.append(record)
    table_props = [
        ('LINEBELOW', (0,0), (-1,0), 1, colors.black),
        ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 10),
        ('FONT', (0,1), (-1,-1), 'Helvetica', 10),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('ALIGN', (-2,0), (-2,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), (None, colors.HexColor(0xf0f0f0))),
        ]
    result = []
    result.append(Platypus_Table(data, repeatRows=1, hAlign="LEFT", colWidths=col_widths, style=TableStyle(table_props)))
    result.append(PageBreak())
    return result

#
# Bestzeiten
#

def create_bestzeiten_doctemplate(wettkampf, disziplin):
    f = Frame(1*cm, 1*cm, PAGE_WIDTH-2*cm, PAGE_HEIGHT-2.5*cm, id='normal')
    pt = PageTemplate(id="Bestzeiten", frames=f, onPageEnd=write_bestzeiten_header_footer)
    doc = BaseDocTemplate(None, pageTemplates=[pt], pagesize=A4)
    doc.wettkampf = wettkampf
    doc.disziplin = disziplin
    return doc

def start_bestzeiten_page(doc, flowables):
    f = Frame(1*cm, 1*cm, PAGE_WIDTH-2*cm, PAGE_HEIGHT-2.5*cm, id='normal')
    pt = PageTemplate(id="Bestzeiten", frames=f, onPageEnd=write_bestzeiten_header_footer)
    doc.addPageTemplates(pt)
    flowables.pop() # Remove last PageBreak
    flowables.append(NextPageTemplate('Bestzeiten'))
    flowables.append(PageBreak())

def write_bestzeiten_header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.drawString(2*cm, PAGE_HEIGHT-1*cm, "Bestzeiten %s" % (doc.disziplin.disziplinart))
    canvas.drawRightString(PAGE_WIDTH-2*cm, PAGE_HEIGHT-1*cm, "%s %d" % (doc.wettkampf.name, doc.wettkampf.jahr()))
    canvas.drawCentredString(PAGE_WIDTH/2, 1*cm, "Seite %d" % (doc.page,))
    canvas.restoreState()

def create_bestzeiten_flowables(posten_name, zeitrangliste):
    data = []
    header = ['Posten', 'Richtzeit', 'Stnr', 'Fahrerpaar', 'Sektion', 'Kat', 'Zeit', 'Note']
    data.append(header)
    col_widths = (30, 45, 30, 140, 80, 30, 40, 30)
    ss = _create_style_sheet()
    for i, row in enumerate(zeitrangliste):
        record = []
        if i == 0:
            record.append(Paragraph(unicode(posten_name), ss['center']))
            record.append(Paragraph(unicode((row['richtzeit'])), ss['center']))
        else:
            record.append(None)
            record.append(None)
        record.append(Paragraph(unicode(row['startnummer']), ss['center']))
        record.append(Paragraph(row['steuermann'] + " / " + row['vorderfahrer'], ss['left']))
        record.append(Paragraph(row['sektion'], ss['left']))
        record.append(Paragraph(row['kategorie'], ss['center']))
        record.append(Paragraph(unicode(row['zeit']), ss['center']))
        record.append(Paragraph(unicode(row['punkte']), ss['right']))
        data.append(record)
    table_props = [
        ('LINEBELOW', (0,0), (-1,0), 1, colors.black),
        ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 8),
        ('FONT', (0,1), (-1,-1), 'Helvetica', 8),
        ('ALIGN', (0,0), (2,-1), 'CENTER'),
        ('ALIGN', (-3,0), (-2,-1), 'CENTER'),
        ('ALIGN', (-1,0), (-1,-1), 'RIGHT'),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), (None, colors.HexColor(0xf0f0f0))),
        ]
    result = []
    result.append(Platypus_Table(data, repeatRows=1, colWidths=col_widths, style=TableStyle(table_props)))
    result.append(Spacer(1, 10))
    return result
