# -*- coding: latin-1 -*-

from django.db import models

SCHIFFS_ART = (
        ('b', 'Boot'),
        ('w', 'Weidling'),
        )

# Stammdaten (importiert)

class Sektion(models.Model):
    name = models.CharField(max_length=50)


class Mitglied(models.Model):
    GESCHLECHT_ART = (
            ('f', 'Frau'),
            ('m', 'Mann'),
            )
    name = models.CharField(max_length=50)
    vorname = models.CharField(max_length=50)
    geburtsdatum = models.DateField()
    geschlecht = models.CharField(max_length=1, choices=GESCHLECHT_ART)
    sektion = models.ForeignKey('Sektion')
    # Für Vater/Sohn respektive Parent/Child Rangliste
    parent = models.ForeignKey('Mitglied')


# Stammdaten/Konfigurationsdaten

DISZIPLIN_ART = (
        (1, 'Einzelfahren'),
        (2, 'Sektionsfahren'),
        (3, 'Bootsfährenbau'),
        (4, 'Einzelschnüren'),
        (5, 'Gruppenschnüren'),
        (6, 'Schwimmen'),
        )

class Disziplinart(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return u'%s' % (self.name,)


POSTEN_ART = (
        # Alt: Variable Posten
        (1, 'Allgemeines und Antreten (Einzelfahren)'),
        (2, 'Abfahrt bei einer Stange'),
        (3, 'Abfahrt unterhalb eines markierten Felsens'),
        (4, 'Umfahren eines markierten Felsens'),
        (5, 'Landung auf bestimmtes Ziel'),
        (6, 'Landung auf höchstes Ziel (Einzelfahren)'),
        (7, 'Einfahren in die Brückenlinie'),
        (8, 'Durchfahrt'),
        (9, 'Zeitnote'), # Ruderfahrt, Stachelfahrt
        (10, 'Anmeldung (Sektionsfahren)'), # Bewertung: JP_Gutschrift
        (11, 'Gemeinsame Stachelfahrt'),
        (13, 'Landung auf höchstes Ziel (Sektionsfahren)'),
        (18, 'Abfahrt und Überfahrt in Linie'),
        (19, 'Landung in Linie'),
        (20, 'Abmeldung'),
        (21, 'Stachelfahrt'),
        # Neu: Fixe Posten
        (50, 'Bootsfährenbau'), # Bewertung: Einbauzeit, Ausbauzeit, Zeitzuschlag
        (51, 'Schwimmen'), # Bewertung: Zeit
        (52, 'Einzelschnüren'), # Bewertung: Zeit, Zeitzuschlag
        (53, 'Gruppenschnüren'), # Bewertung: Zeit, Zeitzuschlag
        )

class Postenart(models.Model):
    name = models.CharField(max_length=50)
    disziplinarten = models.ManyToManyField('Disziplinart')
    einzelfahren = models.BooleanField(default=False)
    sektionsfahren = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s' % (self.name,)


class Bewertungsart(models.Model):
    EINHEIT_TYP = (
            ('PUNKT', 'Punkte'),
            ('ZEIT', 'Zeit'),
            )
    name = models.CharField(max_length=50) # Note, Abzug, Zeit, Ziel, Distanz
    signum = models.SmallIntegerField(default=1) # positiv: +1, negativ: -1
    einheit = models.CharField(max_length=1, choices=EINHEIT_TYP)
    wertebereich = models.CharField(max_length=50) # 1,2-10 oder ganze/gebrochene Sekunden
    defaultwert = models.DecimalField(max_digits=4, decimal_places=2)
    maximalwert = models.DecimalField(max_digits=4, decimal_places=2)
    postenarten = models.ForeignKey('Postenart')

    def __unicode__(self):
        return u'%s' % (self.name,)


class Kategorie(models.Model):
    GESCHLECHT_ART = (
            ('g', 'Gemischt'),
            ('f', 'Frauen'),
            ('m', 'Männer'),
            )
    disziplinart = models.ForeignKey('Disziplinart')
    name = models.CharField(max_length=10)
    alter_von = models.PositiveSmallIntegerField()
    alter_bis = models.PositiveSmallIntegerField()
    geschlecht = models.CharField(max_length=1, choices=GESCHLECHT_ART,
                                  default='g')

    def __unicode__(self):
        return u'%s' % (self.name,)


# Bewegungsdaten


class Wettkampf(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    von = models.DateField()
    bis = models.DateField(blank=True, null=True)

    def __unicode__(self):
        return u'%s' % (self.name,)


class Disziplin(models.Model):
    wettkampf = models.ForeignKey('Wettkampf', editable=False)
    disziplinart = models.ForeignKey('Disziplinart', blank=False, default=1)
    # z.B. "Einzelfahren II/III/C/D/F" oder "Einzelfahren II/III" oder
    # "Sektionsfahren". Default ist der Name der Disziplin.
    name = models.CharField(max_length=20)
    # Mit den hier angegebenen Kategorien kann man bei der Startliste prüfen,
    # dass kein falscher Teilnehmer mitmacht. Zudem kann man den Namen
    # dieser Disziplin basierend auf diesen Kategorien zusammenstellen.
    kategorien = models.ManyToManyField('Kategorie')

    def __unicode__(self):
        return u'%s' % (self.name,)


class Posten(models.Model):
    disziplin = models.ForeignKey('Disziplin')
    postenart = models.ForeignKey('Postenart')
    bezeichnung = models.CharField(max_length=20)


class Bewertung(models.Model):
    bewertungsart = models.ForeignKey('Bewertungsart')
    posten = models.ForeignKey('Posten')
    teilnehmer = models.ForeignKey('Teilnehmer')
    wert = models.DecimalField(max_digits=4, decimal_places=2) # punkte | zeit


class Teilnehmer(models.Model):
    disziplin = models.ForeignKey('Disziplin')
    startnummer = models.PositiveSmallIntegerField()
    disqualifiziert = models.BooleanField(default=False)
    ausgeschieden = models.BooleanField(default=False)


class Person(Teilnehmer):
    """Schwimmer/Schnürer"""
    mitglied = models.ForeignKey('Mitglied')
    sektion = models.ForeignKey('Sektion')
    kategorie = models.ForeignKey('Kategorie')


class Gruppe(Teilnehmer):
    """Schnürgruppe/Bootfähre/Sektion"""
    chef = models.ForeignKey('Mitglied')
    sektion = models.ForeignKey('Sektion')
    name = models.CharField(max_length=20) # z.B. Bremgarten I


class Schiffsektion(Teilnehmer):
    """Startnummer entspricht position 1,2,3,... innerhalb Gruppe"""
    # schiffsart abgeleitet von Eingabe Anzahl Boote/Weidlinge
    schiffsart = models.CharField(max_length=1, choices=SCHIFFS_ART)
    gruppe = models.ForeignKey('Gruppe')


class Schiffeinzel(Teilnehmer):
    """Doppelstarter werden automatisch bei Erstellung der Rangliste gesucht"""
    steuermann = models.ForeignKey('Mitglied', related_name='steuermann')
    vorderfahrer = models.ForeignKey('Mitglied', related_name='vorderfahrer')
    sektion = models.ForeignKey('Sektion')
    kategorie = models.ForeignKey('Kategorie')
    # schiffsart abgeleitet von Kategorie
    schiffsart = models.CharField(max_length=1, choices=SCHIFFS_ART)


# Hilfstabellen für Ranglisten

class Richtzeit(models.Model):
    posten = models.ForeignKey('Posten')
    zeit = models.DecimalField(max_digits=4, decimal_places=2)


class Kranzlimite(models.Model):
    disziplin = models.ForeignKey('Disziplin')
    kategorie = models.ForeignKey('Kategorie')
    # Dieses Attribut ist für das Rechnungsbüro einfacher einzugeben als
    # ein Prozentsatz. Default ist 25%, falls Wert NULL ist.
    letzter_kranzrang = models.DecimalField(max_digits=2, decimal_places=0)
