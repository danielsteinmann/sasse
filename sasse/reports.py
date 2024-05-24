# -*- coding: utf-8 -*-

from .templatetags.sasse import zeit2str
from django.conf import settings

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
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

def _get_spsv_logo():
    # STATIC_ROOT is a python 'Path' object
    return settings.STATIC_ROOT / 'sasse/spsv-logo.jpg'

def _create_style_sheet(baseFontSize=8):
    stylesheet = StyleSheet1()
    stylesheet.add(ParagraphStyle(name='left', fontName='Helvetica',
        fontSize=baseFontSize, alignment=TA_LEFT, splitLongWords=False))
    stylesheet.add(ParagraphStyle('center', parent=stylesheet['left'], alignment=TA_CENTER, splitLongWords=False))
    stylesheet.add(ParagraphStyle('right', parent=stylesheet['left'], alignment=TA_RIGHT, splitLongWords=False))
    return stylesheet

def _extract_jahrgang(geburtstag):
    return ' <font size=-2>' + geburtstag.strftime('%Y') + "</font>"

def create_rangliste_doctemplate(wettkampf):
    f = Frame(1*cm, 1*cm, PAGE_WIDTH-2*cm, PAGE_HEIGHT-3*cm, id='normal')
    pt = PageTemplate(id="Rangliste", frames=f, onPageEnd=write_rangliste_header_footer)
    doc = BaseDocTemplate(None, pageTemplates=[pt], pagesize=A4)
    doc.wettkampf = wettkampf
    return doc

def write_rangliste_header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.drawImage(_get_spsv_logo(), 2*cm, PAGE_HEIGHT-2*cm, width=1.5*cm, height=1.5*cm)
    canvas.line(4*cm, PAGE_HEIGHT-1.2*cm, PAGE_WIDTH-2*cm, PAGE_HEIGHT-1.2*cm)
    canvas.drawString(4*cm, PAGE_HEIGHT-1*cm, doc.docEval("header_line"))
    canvas.drawRightString(PAGE_WIDTH-2*cm, PAGE_HEIGHT-1*cm, "%s %d" % (doc.wettkampf.name, doc.wettkampf.jahr()))
    canvas.drawString(2*cm, 1*cm, "https://ranglisten.pontonier.ch")
    canvas.drawRightString(PAGE_WIDTH-2*cm, 1*cm, "Seite %d" % (doc.page,))
    canvas.restoreState()

def create_rangliste_header(text):
    return DocExec("header_line = '%s'" % (text,))

def create_rangliste_flowables(rangliste, kranzlimite, disziplin, kategorie):
    data = [['Rang', 'Steuermann', 'Vorderfahrer', 'Sektion', 'Stnr', 'Zeit', 'Punkte']]
    col_widths = (30, 140, 140, 80, 30, 40, 30)
    anzahl_ohne_kranz = 0
    ds_marker = '<font size=-2> (DS)</font>'
    ss = _create_style_sheet()
    for row in rangliste:
        if not row['kranz']: anzahl_ohne_kranz += 1
        if row['steuermann_ist_ds']: row['steuermann'] += ds_marker
        if row['vorderfahrer_ist_ds']: row['vorderfahrer'] += ds_marker
        row['steuermann'] += _extract_jahrgang(row['steuermann_jg'])
        row['vorderfahrer'] += _extract_jahrgang(row['vorderfahrer_jg'])
        record = []
        record.append(Paragraph(str(row['rang']), ss['center']))
        record.append(Paragraph(row['steuermann'], ss['left']))
        record.append(Paragraph(row['vorderfahrer'], ss['left']))
        record.append(Paragraph(row['sektion'], ss['left']))
        record.append(Paragraph(str(row['startnummer']), ss['center']))
        record.append(Paragraph(str(row['zeit_tot']), ss['center']))
        record.append(Paragraph(str(row['punkt_tot']), ss['center']))
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
    header = "Rangliste %s, Kategorie %s" % (disziplin.disziplinart.name, kategorie.name)
    result = []
    result.append(create_rangliste_header(header))
    result.append(Platypus_Table(data, repeatRows=1, colWidths=col_widths, style=TableStyle(table_props)))
    result.append(PageBreak())
    return result


#
# Notenblatt
#

def create_notenblatt_doctemplate(wettkampf, disziplin):
    f = Frame(2*cm, 1*cm, PAGE_WIDTH-2*cm, PAGE_HEIGHT-3.5*cm, id='normal')
    pt = PageTemplate(id="Notenblatt", frames=f, onPageEnd=write_notenblatt_header_footer)
    doc = BaseDocTemplate(None, pageTemplates=[pt], pagesize=A4)
    doc.wettkampf = wettkampf
    doc.disziplin = disziplin
    return doc

def write_notenblatt_header_footer(canvas, doc):
    canvas.saveState()
    canvas.drawImage(_get_spsv_logo(), 2.2*cm, PAGE_HEIGHT-2*cm, width=1.5*cm, height=1.5*cm)
    canvas.line(4*cm, PAGE_HEIGHT-1.3*cm, PAGE_WIDTH-2*cm, PAGE_HEIGHT-1.3*cm)
    canvas.setFont('Helvetica', 8)
    canvas.drawString(4*cm, PAGE_HEIGHT-1.1*cm, "Notenblatt %s" % (doc.disziplin.disziplinart))
    canvas.drawRightString(PAGE_WIDTH-2*cm, PAGE_HEIGHT-1.1*cm, "%s %d" % (doc.wettkampf.name, doc.wettkampf.jahr()))
    canvas.restoreState()

def create_notenblatt_flowables(posten_werte, schiffeinzel):
    result = []
    ss = _create_style_sheet(baseFontSize=10)
    # --------
    steuermann = schiffeinzel.steuermann
    vorderfahrer = schiffeinzel.vorderfahrer
    data = [
            ["Startnummer:", str(schiffeinzel.startnummer)],
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
    # --------
    special_text = None
    if schiffeinzel.ausgeschieden:
        special_text = "Ausgeschieden"
    elif schiffeinzel.disqualifiziert:
        special_text = "Disqualifiziert!"
    if special_text:
        result.append(Paragraph(special_text, ss['center']))
    result.append(Spacer(1, 30))
    # --------
    data = [['Posten', 'Übungsteil', 'Abzug', 'Note', 'Zeit', 'Punkte',]]
    col_widths = (40, 260, 40, 40, 55, 40)
    for row in posten_werte:
        record = []
        if row.get('posten'):
            record.append(Paragraph(row['posten'], ss['center']))
            if row['posten_art'] == "Zeitnote":
                row['posten_art'] += " <font size=-2>(Richtzeit " + str(row['richtzeit']) + ")</font>"
            record.append(Paragraph(row['posten_art'], ss['left']))
            record.append(str(row['abzug']))
            record.append(str(row['note']))
            record.append(str(row['zeit']))
            record.append(str(row['punkte']))
        else:
            for i in range(0,4): record.append("")
            record.append(str(row['zeit']))
            record.append(str(row['punkte']))
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
    f = Frame(1*cm, 1*cm, PAGE_WIDTH-2*cm, PAGE_HEIGHT-3.5*cm, id='normal')
    pt = PageTemplate(id="Startliste", frames=f, onPageEnd=write_startliste_header_footer)
    doc = BaseDocTemplate(None, pageTemplates=[pt], pagesize=A4)
    doc.wettkampf = wettkampf
    doc.disziplin = disziplin
    return doc

def write_startliste_header_footer(canvas, doc):
    canvas.saveState()
    canvas.drawImage(_get_spsv_logo(), 1.2*cm, PAGE_HEIGHT-2*cm, width=1.5*cm, height=1.5*cm)
    canvas.line(3*cm, PAGE_HEIGHT-1.3*cm, PAGE_WIDTH-1*cm, PAGE_HEIGHT-1.3*cm)
    canvas.setFont('Helvetica-Bold', 10)
    canvas.drawString(3*cm, PAGE_HEIGHT-1.1*cm, "Startliste %s" % (doc.disziplin.disziplinart))
    canvas.drawRightString(PAGE_WIDTH-1*cm, PAGE_HEIGHT-1.1*cm, "%s %d" % (doc.wettkampf.name, doc.wettkampf.jahr()))
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
        record.append(Paragraph(str(s.startnummer), ss['center']))
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

def create_bestzeiten_flowables(all_ranglisten, disziplin):
    header = "Bestzeiten %s" % (disziplin.name)
    result = []
    result.append(create_rangliste_header(header))
    for posten_name, zeitrangliste in all_ranglisten:
        flowables = _create_bestzeiten_flowables_posten(posten_name, zeitrangliste)
        result.extend(flowables)
    result.append(PageBreak())
    return result

def _create_bestzeiten_flowables_posten(posten_name, zeitrangliste):
    data = []
    header = ['Posten', 'Richtzeit', 'Stnr', 'Fahrerpaar', 'Sektion', 'Kat', 'Zeit', 'Note']
    data.append(header)
    col_widths = (30, 45, 30, 140, 80, 30, 40, 30)
    ss = _create_style_sheet()
    for i, row in enumerate(zeitrangliste):
        record = []
        if i == 0:
            record.append(Paragraph(str(posten_name), ss['center']))
            record.append(Paragraph(str((row['richtzeit'])), ss['center']))
        else:
            record.append(None)
            record.append(None)
        record.append(Paragraph(str(row['startnummer']), ss['center']))
        record.append(Paragraph(row['steuermann'] + " / " + row['vorderfahrer'], ss['left']))
        record.append(Paragraph(row['sektion'], ss['left']))
        record.append(Paragraph(row['kategorie'], ss['center']))
        record.append(Paragraph(str(row['zeit']), ss['center']))
        record.append(Paragraph(str(row['note']), ss['right']))
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

#
# Notenliste
#

def create_notenliste_doctemplate(wettkampf, disziplin):
    f = Frame(1*cm, 1*cm, PAGE_HEIGHT-2*cm, PAGE_WIDTH-3.3*cm, id='normal')
    pt = PageTemplate(id="Bestzeiten", frames=f, onPageEnd=write_notenliste_header_footer)
    doc = BaseDocTemplate(None, pageTemplates=[pt], pagesize=landscape(A4))
    doc.wettkampf = wettkampf
    doc.disziplin = disziplin
    return doc

def write_notenliste_header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.drawImage(_get_spsv_logo(), 2*cm, PAGE_WIDTH-2*cm, width=1.5*cm, height=1.5*cm)
    canvas.line(4*cm, PAGE_WIDTH-1.2*cm, PAGE_HEIGHT-2*cm, PAGE_WIDTH-1.2*cm)
    canvas.drawString(4*cm, PAGE_WIDTH-1*cm, "Notenliste %s" % (doc.disziplin.disziplinart))
    canvas.drawCentredString(PAGE_HEIGHT/2, PAGE_WIDTH-1*cm, "Sektion %s" % (doc.docEval("sektion_name")))
    canvas.drawRightString(PAGE_HEIGHT-2*cm, PAGE_WIDTH-1*cm, "%s %d" % (doc.wettkampf.name, doc.wettkampf.jahr()))
    canvas.drawCentredString(PAGE_HEIGHT/2, 1*cm, "Seite %d" % (doc.page,))
    canvas.restoreState()

def create_notenliste_flowables(posten, notenliste, sektion=None):
    data = []
    posten_header = []
    posten_header_width = []
    for p in posten:
        posten_header.append(p.name)
        posten_header_width.append(28)
        if p.postenart.name == "Zeitnote":
            posten_header.append(p.name + "[s]")
            posten_header_width.append(35)
    header = ['Stnr', 'Fahrerpaar', 'Kat'] + posten_header + ['Zeit', 'Punkte']
    data.append(header)
    col_widths = [30, 130, 30] + posten_header_width + [40, 30]
    ss = _create_style_sheet()
    for i, row in enumerate(notenliste):
        record = []
        record.append(Paragraph(str(row['startnummer']), ss['center']))
        fahrerpaar = row['steuermann'] + " / " + row['vorderfahrer']
        if not sektion:
            fahrerpaar += " - " + row['sektion']
        record.append(Paragraph(fahrerpaar, ss['left']))
        record.append(Paragraph(row['kategorie'], ss['center']))
        for note in row['noten']:
            if note.bewertungsart.einheit == "ZEIT":
                record.append(Paragraph('<font size="-2">' + str(note) + '</font>', ss['right']))
            else:
                record.append(Paragraph(str(note), ss['right']))
        record.append(Paragraph(str(row['zeit_tot']), ss['center']))
        record.append(Paragraph(str(row['punkt_tot']), ss['right']))
        data.append(record)
    table_props = [
        ('LINEBELOW', (0,0), (-1,0), 1, colors.black),
        ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 8),
        ('FONT', (0,1), (-1,-1), 'Helvetica', 8),
        ('ALIGN', (0,0), (1,-1), 'CENTER'),
        ('ALIGN', (1,0), (1,-1), 'LEFT'),
        ('ALIGN', (2,0), (2,-1), 'CENTER'),
        ('ALIGN', (3,0), (-1,-1), 'RIGHT'),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), (None, colors.HexColor(0xf0f0f0))),
        ]
    result = []
    sektion_name = ""
    if sektion:
        sektion_name = sektion.name
    result.append(DocExec("sektion_name = '%s'" % sektion_name))
    result.append(Platypus_Table(data, repeatRows=1, colWidths=col_widths, style=TableStyle(table_props)))
    result.append(Spacer(1, 10))
    result.append(PageBreak())
    return result

#
# Notenblatt Sektionsfahren
#

def create_sektionsfahren_notenblatt_doctemplate(wettkampf, disziplin):
    f = Frame(1*cm, 1*cm, PAGE_WIDTH-2*cm, PAGE_HEIGHT-3.5*cm, id='normal')
    pt = PageTemplate(id="Notenblatt", frames=f, onPageEnd=write_sektionsfahren_notenblatt_header_footer)
    doc = BaseDocTemplate(None, pageTemplates=[pt], pagesize=A4)
    doc.wettkampf = wettkampf
    doc.disziplin = disziplin
    return doc

def write_sektionsfahren_notenblatt_header_footer(canvas, doc):
    canvas.saveState()
    canvas.drawImage(_get_spsv_logo(), 1.2*cm, PAGE_HEIGHT-2*cm, width=1.5*cm, height=1.5*cm)
    canvas.line(3*cm, PAGE_HEIGHT-1.3*cm, PAGE_WIDTH-2*cm, PAGE_HEIGHT-1.3*cm)
    canvas.setFont('Helvetica', 8)
    canvas.drawString(3*cm, PAGE_HEIGHT-1.1*cm, "Notenblatt %s" % (doc.disziplin.disziplinart))
    canvas.drawRightString(PAGE_WIDTH-2*cm, PAGE_HEIGHT-1.1*cm, "%s %d" % (doc.wettkampf.name, doc.wettkampf.jahr()))
    canvas.restoreState()

def create_sektionsfahren_notenblatt_flowables(sektion):
    result = []
    ss = _create_style_sheet(baseFontSize=10)
    gewichtet_text = "(%s / %d)" % (sektion['gewichtet'], sektion['anz_schiffe'])
    data = [
            [sektion['name'], " "],
            ["Durchschnitt gewichtet:", sektion['gewichtet_avg'], gewichtet_text],
            ["Abzüge Sektionstotal:", sektion['abzug']],
            ["Sektionstotal:", sektion['total']],
            ]
    col_widths = (120, 60, 300)
    table_props = [
        ('FONT', (0,0), (-1,-1), 'Helvetica', 10),
        ('LINEBELOW', (0,0), (1,0), 1, colors.grey),
        ('FONT', (0,0), (0,0), 'Helvetica-Bold', 10),
        ('FONT', (1,3), (1,3), 'Helvetica-Bold', 10),
        ('FONT', (-1,0), (-1,-1), 'Helvetica', 8),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ]
    result.append(Platypus_Table(data, hAlign="LEFT", colWidths=col_widths, style=TableStyle(table_props)))
    result.append(Spacer(1, 20))
    # ----
    data = [['Gruppe', 'Schiffe', 'Punkte', 'Gewichtet', 'Abzug', 'Bemerkung']]
    col_widths = (120, 50, 60, 60, 40, 150)
    ss = _create_style_sheet(10)
    table_props = [
        ('LINEBELOW', (0,0), (-1,0), 1, colors.black),
        ('LINEABOVE', (0,-1), (-1,-1), 1, colors.black),
        ('FONT', (0,0), (-1,-1), 'Helvetica', 10),
        ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 10),
        ('FONT', (0,-1), (-1,-1), 'Helvetica-Bold', 10),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('ALIGN', (1,0), (4,-1), 'RIGHT'),
        ]
    for gruppe in sektion['gruppen']:
        record = []
        record.append(gruppe.name)
        record.append(gruppe.anz_schiffe())
        record.append(gruppe.total)
        record.append(gruppe.gewichtet)
        record.append(gruppe.abzug_sektion)
        record.append(gruppe.abzug_sektion_comment)
        data.append(record)
    summary = []
    summary.append("")
    summary.append(sektion['anz_schiffe'])
    summary.append("")
    summary.append(sektion['gewichtet'])
    summary.append(sektion['abzug'])
    data.append(summary)
    result.append(Platypus_Table(data, hAlign="LEFT", colWidths=col_widths, style=TableStyle(table_props)))
    result.append(Spacer(1, 30))
    return result

#
# Notenblatt Gruppe Sektionsfahren
#

def create_sektionsfahren_notenblatt_gruppe_doctemplate(wettkampf, disziplin):
    f = Frame(1*cm, 1*cm, PAGE_WIDTH-2*cm, PAGE_HEIGHT-3.5*cm, id='normal')
    pt = PageTemplate(id="Notenblatt", frames=f, onPageEnd=write_sektionsfahren_notenblatt_gruppe_header_footer)
    doc = BaseDocTemplate(None, pageTemplates=[pt], pagesize=A4)
    doc.wettkampf = wettkampf
    doc.disziplin = disziplin
    return doc

def write_sektionsfahren_notenblatt_gruppe_header_footer(canvas, doc):
    canvas.saveState()
    canvas.drawImage(_get_spsv_logo(), 1.2*cm, PAGE_HEIGHT-2*cm, width=1.5*cm, height=1.5*cm)
    canvas.line(3*cm, PAGE_HEIGHT-1.3*cm, PAGE_WIDTH-2*cm, PAGE_HEIGHT-1.3*cm)
    canvas.setFont('Helvetica', 8)
    canvas.drawString(3*cm, PAGE_HEIGHT-1.1*cm, "Notenblatt %s" % (doc.disziplin.disziplinart))
    canvas.drawRightString(PAGE_WIDTH-2*cm, PAGE_HEIGHT-1.1*cm, "%s %d" % (doc.wettkampf.name, doc.wettkampf.jahr()))
    canvas.restoreState()

def create_sektionsfahren_notenblatt_gruppe_flowables(gruppe, notenliste):
    result = []
    ss = _create_style_sheet(baseFontSize=10)
    # --------
    zuschlag_text = "2 * (%d JP + %d Frauen + %d Senioren) / Anzahl Schiffe" % (gruppe.anz_jps(), gruppe.anz_frauen(), gruppe.anz_senioren())
    data = [
            [gruppe.name, " "],
            ["Durchschnitt Punkte:", gruppe.gefahren],
            ["Durchschnitt Zuschläge:", gruppe.zuschlag, zuschlag_text],
            ["Abzüge Gruppentotal:", gruppe.abzug_gruppe, gruppe.abzug_gruppe_comment],
            ["Total:", gruppe.total],
            ]
    if gruppe.abzug_sektion:
        data.append(["Abzüge Sektionstotal:", gruppe.abzug_sektion, gruppe.abzug_sektion_comment])
    col_widths = (120, 60, 300)
    table_props = [
        ('FONT', (0,0), (-1,-1), 'Helvetica', 10),
        ('LINEBELOW', (0,0), (1,0), 1, colors.grey),
        ('FONT', (0,0), (0,0), 'Helvetica-Bold', 10),
        ('FONT', (1,4), (1,4), 'Helvetica-Bold', 10),
        ('FONT', (-1,0), (-1,-1), 'Helvetica', 8),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ]
    result.append(Platypus_Table(data, hAlign="LEFT", colWidths=col_widths, style=TableStyle(table_props)))
    result.append(Spacer(1, 10))
    # ------
    data = []
    headers = ['', '']
    schiff_range = list(range(1, gruppe.anz_schiffe() + 1))
    for i in schiff_range:
        headers.append("%d. Schiff" % i)
        headers.append("")
    data.append(headers)
    headers = ["", ""]
    for i in schiff_range:
        headers.append("1.DG")
        headers.append("2.DG")
    data.append(headers)
    col_widths = [30, 210]
    for i in schiff_range:
        col_widths.append(30)
        col_widths.append(30)
    rows_with_spans = {}
    for n, row in enumerate(notenliste):
        record = []
        if row.get('posten'):
            record.append(Paragraph(row['posten'], ss['center']))
            record.append(Paragraph(row['postenart'], ss['left']))
        else:
            record.append("")
            record.append("")
        colspan = row.get('colspan')
        if colspan > 1:
            rows_with_spans[n] = colspan
        for note in row['noten']:
            record.append(str(note))
            for i in range(1, colspan):
                record.append("")
        data.append(record)
    table_props = [
        ('GRID', (0,2), (-1,-2), 0.5, colors.grey),
        ('GRID', (2,0), (-1,-1), 0.5, colors.grey),
        ('FONT', (0,0), (-1,-1), 'Helvetica', 10),
        ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 10),
        ('FONT', (0,-1), (-1,-1), 'Helvetica-Bold', 10),
        ('FONT', (0,1), (-1,1), 'Helvetica', 8),
        ('ALIGN', (2,0), (-1,-1), 'CENTER'),
        ('LINEBELOW', (0,1), (-1,1), 1, colors.black),
        ('LINEABOVE', (0,-1), (-1,-1), 1, colors.black),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), (None, colors.HexColor(0xf0f0f0))),
        ]
    for i in schiff_range:
        # Header row
        table_props.extend([('SPAN', (i*2,0), ((i*2)+1,0))])
    for row, span in rows_with_spans.items():
        # Body rows (offset by 2 because of 2 header rows)
        for i in schiff_range:
            table_props.extend([('SPAN', (i*2,row+2), ((i*2)+span-1,row+2))])
    result.append(Platypus_Table(data, hAlign="LEFT", colWidths=col_widths, style=TableStyle(table_props)))
    result.append(PageBreak())
    return result

#
# Rangliste Sektionsfahren
#

def create_sektionsfahren_rangliste_flowables(rangliste, disziplin):
    data = [['Kranz', 'Rang', 'Sektion', 'Gruppen', 'Schiffe', 'JP', 'Fr.', 'Sen.', 'Total']]
    col_widths = (50, 40, 110, 50, 40, 30, 30, 30, 70)
    ss = _create_style_sheet(10)
    table_props = [
        ('LINEBELOW', (0,0), (-1,0), 1, colors.black),
        ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 10),
        ('FONT', (0,1), (-1,-1), 'Helvetica', 10),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('ALIGN', (3,0), (-1,-1), 'CENTER'),
        ]
    kranz_typ = None
    for i, row in enumerate(rangliste):
        if row['kranz_typ'] == kranz_typ:
            # Zeige Kranztyp nur wenn Wert wechselt
            row['kranz_typ'] = ""
        else:
            kranz_typ = row['kranz_typ']
            if i > 0:
                table_props.extend([
                    ('LINEBELOW', (0,i), (-1,i), 1, colors.black),
                    ('BOTTOMPADDING', (0,i), (-1,i), 10),
                    ])
        record = []
        record.append(Paragraph(row['kranz_typ'], ss['left']))
        record.append(Paragraph(str(row['rang']), ss['center']))
        record.append(Paragraph(row['name'], ss['left']))
        record.append(Paragraph(str(row['anz_gruppen']), ss['center']))
        record.append(Paragraph(str(row['anz_schiffe']), ss['center']))
        record.append(Paragraph(str(row['anz_jps']), ss['center']))
        record.append(Paragraph(str(row['anz_frauen']), ss['center']))
        record.append(Paragraph(str(row['anz_senioren']), ss['center']))
        record.append(Paragraph(str(row['total']), ss['center']))
        data.append(record)
    header = "Rangliste %s" % disziplin.disziplinart.name
    result = []
    result.append(create_rangliste_header(header))
    result.append(Platypus_Table(data, repeatRows=1, colWidths=col_widths, style=TableStyle(table_props)))
    result.append(PageBreak())
    return result


#
# Schwimmen
#

def create_schwimmen_rangliste_flowables(rangliste, kranzlimite, disziplin, kategorie):
    data = [['Rang', 'Schwimmer', 'Sektion', 'Zeit']]
    col_widths = (30, 140, 80, 40)
    anzahl_ohne_kranz = 0
    ss = _create_style_sheet()
    for row in rangliste:
        if not row.kranz: anzahl_ohne_kranz += 1
        schwimmer = row.mitglied
        record = []
        record.append(Paragraph(str(row.rang), ss['center']))
        record.append(Paragraph(schwimmer.name + " " + schwimmer.vorname + _extract_jahrgang(schwimmer.geburtsdatum), ss['left']))
        record.append(Paragraph(schwimmer.sektion.name, ss['left']))
        record.append(Paragraph(str(zeit2str(row.zeit)), ss['center']))
        data.append(record)
    table_props = [
        ('LINEBELOW', (0,0), (-1,0), 1, colors.black),
        ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 8),
        ('FONT', (0,1), (-1,-1), 'Helvetica', 8),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('ALIGN', (1,0), (2,-1), 'LEFT'),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('ALIGN', (-1,0), (-1,-1), 'CENTER'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), (None, colors.HexColor(0xf0f0f0))),
        ]
    if anzahl_ohne_kranz and kranzlimite:
        kranzlimite_row = len(data) - anzahl_ohne_kranz
        text = Paragraph('Kranzlimite: %s ' % (zeit2str(kranzlimite)), ss['left'])
        data.insert(kranzlimite_row, [text, None, None, None])
        table_props.extend([
            ('SPAN', (0,kranzlimite_row), (-1,kranzlimite_row)),
            ('BACKGROUND', (0,kranzlimite_row), (-1,kranzlimite_row), colors.lightgrey),
            ])
    header = "Rangliste %s, Kategorie %s" % (disziplin.disziplinart.name, kategorie)
    result = []
    result.append(create_rangliste_header(header))
    result.append(Platypus_Table(data, repeatRows=1, colWidths=col_widths, style=TableStyle(table_props)))
    result.append(PageBreak())
    return result


#
# Einzelschnüren
#

def create_einzelschnueren_rangliste_flowables(rangliste, kranzlimite, disziplin, kategorie):
    data = [['Rang', 'Schnürer', 'Sektion', 'Parcourszeit', 'Zuschläge', 'Totalzeit']]
    col_widths = (30, 140, 80, 60, 50, 60)
    anzahl_ohne_kranz = 0
    ss = _create_style_sheet()
    for row in rangliste:
        if not row.kranz: anzahl_ohne_kranz += 1
        schnuerer = row.mitglied
        record = []
        record.append(Paragraph(str(row.rang), ss['center']))
        record.append(Paragraph(schnuerer.name + " " + schnuerer.vorname + _extract_jahrgang(schnuerer.geburtsdatum), ss['left']))
        record.append(Paragraph(schnuerer.sektion.name, ss['left']))
        record.append(Paragraph(str(zeit2str(row.parcourszeit)), ss['center']))
        record.append(Paragraph(str(row.zuschlaege), ss['center']))
        record.append(Paragraph(str(zeit2str(row.zeit)), ss['center']))
        data.append(record)
    table_props = [
        ('LINEBELOW', (0,0), (-1,0), 1, colors.black),
        ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 8),
        ('FONT', (0,1), (-1,-1), 'Helvetica', 8),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('ALIGN', (1,0), (2,-1), 'LEFT'),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('ALIGN', (-3,0), (-1,-1), 'CENTER'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), (None, colors.HexColor(0xf0f0f0))),
        ]
    if anzahl_ohne_kranz and kranzlimite:
        kranzlimite_row = len(data) - anzahl_ohne_kranz
        text = Paragraph('Kranzlimite: %s ' % (zeit2str(kranzlimite)), ss['left'])
        data.insert(kranzlimite_row, [text, None, None, None, None, None])
        table_props.extend([
            ('SPAN', (0,kranzlimite_row), (-1,kranzlimite_row)),
            ('BACKGROUND', (0,kranzlimite_row), (-1,kranzlimite_row), colors.lightgrey),
            ])
    header = "Rangliste %s, Kategorie %s" % (disziplin.disziplinart.name, kategorie)
    result = []
    result.append(create_rangliste_header(header))
    result.append(Platypus_Table(data, repeatRows=1, colWidths=col_widths, style=TableStyle(table_props)))
    result.append(PageBreak())
    return result


#
# Gruppenschnüren
#

def create_gruppenschnueren_rangliste_flowables(rangliste, kranzlimite, disziplin, kategorie):
    data = [['Rang', 'Gruppe', 'Aufbauzeit', 'Abbauzeit', 'Zuschläge', 'Totalzeit']]
    col_widths = (30, 110, 60, 60, 50, 60)
    anzahl_ohne_kranz = 0
    ss = _create_style_sheet(10)
    for row in rangliste:
        if not row.kranz: anzahl_ohne_kranz += 1
        record = []
        record.append(Paragraph(str(row.rang), ss['center']))
        record.append(Paragraph(row.name, ss['left']))
        record.append(Paragraph(str(zeit2str(row.aufbauzeit)), ss['center']))
        record.append(Paragraph(str(zeit2str(row.abbauzeit)), ss['center']))
        record.append(Paragraph(str(row.zuschlaege), ss['center']))
        record.append(Paragraph(str(zeit2str(row.zeit)), ss['center']))
        data.append(record)
    table_props = [
        ('LINEBELOW', (0,0), (-1,0), 1, colors.black),
        ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 10),
        ('FONT', (0,1), (-1,-1), 'Helvetica', 10),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('ALIGN', (1,0), (2,-1), 'LEFT'),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('ALIGN', (-4,0), (-1,-1), 'CENTER'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), (None, colors.HexColor(0xf0f0f0))),
        ]
    if anzahl_ohne_kranz and kranzlimite:
        kranzlimite_row = len(data) - anzahl_ohne_kranz
        text = Paragraph('Kranzlimite: %s ' % (zeit2str(kranzlimite)), ss['left'])
        data.insert(kranzlimite_row, [text, None, None, None, None, None])
        table_props.extend([
            ('SPAN', (0,kranzlimite_row), (-1,kranzlimite_row)),
            ('BACKGROUND', (0,kranzlimite_row), (-1,kranzlimite_row), colors.lightgrey),
            ])
    header = "Rangliste %s, Kategorie %s" % (disziplin.disziplinart.name, kategorie)
    result = []
    result.append(create_rangliste_header(header))
    result.append(Platypus_Table(data, repeatRows=1, colWidths=col_widths, style=TableStyle(table_props)))
    result.append(PageBreak())
    return result


#
# Bootfährenbau
#

def create_bootfaehrenbau_rangliste_flowables(rangliste, kranzlimite, disziplin):
    data = [['Rang', 'Gruppe', 'Einbauzeit', 'Ausbauzeit', 'Zuschläge', 'Totalzeit']]
    col_widths = (30, 110, 60, 60, 50, 60)
    anzahl_ohne_kranz = 0
    ss = _create_style_sheet(10)
    for row in rangliste:
        if not row.kranz: anzahl_ohne_kranz += 1
        record = []
        record.append(Paragraph(str(row.rang), ss['center']))
        record.append(Paragraph(row.name, ss['left']))
        record.append(Paragraph(str(zeit2str(row.einbauzeit)), ss['center']))
        record.append(Paragraph(str(zeit2str(row.ausbauzeit)), ss['center']))
        record.append(Paragraph(str(row.zuschlaege), ss['center']))
        record.append(Paragraph(str(zeit2str(row.zeit)), ss['center']))
        data.append(record)
    table_props = [
        ('LINEBELOW', (0,0), (-1,0), 1, colors.black),
        ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 10),
        ('FONT', (0,1), (-1,-1), 'Helvetica', 10),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('ALIGN', (1,0), (2,-1), 'LEFT'),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('ALIGN', (-4,0), (-1,-1), 'CENTER'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), (None, colors.HexColor(0xf0f0f0))),
        ]
    if anzahl_ohne_kranz and kranzlimite:
        kranzlimite_row = len(data) - anzahl_ohne_kranz
        text = Paragraph('Kranzlimite: %s ' % (zeit2str(kranzlimite)), ss['left'])
        data.insert(kranzlimite_row, [text, None, None, None, None, None])
        table_props.extend([
            ('SPAN', (0,kranzlimite_row), (-1,kranzlimite_row)),
            ('BACKGROUND', (0,kranzlimite_row), (-1,kranzlimite_row), colors.lightgrey),
            ])
    header = "Rangliste %s" % (disziplin.disziplinart.name)
    result = []
    result.append(create_rangliste_header(header))
    result.append(Platypus_Table(data, repeatRows=1, colWidths=col_widths, style=TableStyle(table_props)))
    result.append(PageBreak())
    return result

