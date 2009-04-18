# -*- coding: utf-8 -*-

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
    name = models.CharField(max_length=50, unique_for_year='von')
    zusatz = models.CharField(max_length=100)
    von = models.DateField(help_text="Format: JJJJ-MM-DD")
    bis = models.DateField(null=True, blank=True, help_text="(optional)")

    class Meta:
        ordering = ['-von']

    def __unicode__(self):
        return u'%s' % (self.name,)

    def jahr(self):
        return self.von.year


class Disziplin(models.Model):
    """
    Mit Hilfe der Kategorien kann man bei der Startliste prüfen, dass kein
    falscher Teilnehmer mitmacht. Zudem kann man den Namen dieser Disziplin
    basierend auf diesen Kategorien zusammenstellen.

    Der Name ist z.B. "Einzelfahren II/III/C/D/F", "Einzelfahren II/III",
    "Einzelfahren Plausch" oder "Sektionsfahren". Default ist der Name der
    Disziplin plus Kategorien (falls vorhanden).
    """
    wettkampf = models.ForeignKey('Wettkampf')
    name = models.SlugField(max_length=50)
    disziplinart = models.ForeignKey('Disziplinart', blank=False, default=1)
    kategorien = models.ManyToManyField('Kategorie', null=True, blank=True)

    def __unicode__(self):
        return u'%s' % (self.name,)

    class Meta:
        unique_together = ['wettkampf', 'name']
        ordering = ['name']


class Posten(models.Model):
    disziplin = models.ForeignKey('Disziplin')
    name = models.CharField(max_length=10)
    postenart = models.ForeignKey('Postenart')
    reihenfolge = models.PositiveIntegerField()

    class Meta:
        unique_together = ['disziplin', 'name']
        ordering = ['reihenfolge']



class Bewertung(models.Model):
    """
    Wert ist entweder Anzahl Punkte oder Zeit in Hundertstel Sekunden.
    """
    bewertungsart = models.ForeignKey('Bewertungsart')
    posten = models.ForeignKey('Posten')
    teilnehmer = models.ForeignKey('Teilnehmer')
    wert = models.DecimalField(max_digits=4, decimal_places=2)


class Teilnehmer(models.Model):
    """
    Die gemeinsamen Attribute für einen Teilnehmer an einem Wettkampf.
    """
    disziplin = models.ForeignKey('Disziplin')
    startnummer = models.PositiveIntegerField()
    disqualifiziert = models.BooleanField(default=False)
    ausgeschieden = models.BooleanField(default=False)

    class Meta:
        unique_together = ['disziplin', 'startnummer']


class Person(Teilnehmer):
    """
    Ein Schwimmer oder Schnürer.
    """
    mitglied = models.ForeignKey('Mitglied')
    sektion = models.ForeignKey('Sektion')
    kategorie = models.ForeignKey('Kategorie')


class Gruppe(Teilnehmer):
    """
    Eine Schnürgruppe, eine Bootfährenbautrupp oder eine Sektion beim
    Sektionsfahren.

    Beim Erstellen der Startliste für ein Sektionsfahren wird nach Anzahl
    Booten und Weidlingen gefragt. Diese Zahlen werden beim Speichern benutzt,
    um die entsprechende Anzahl 'Schiffsektion' Records in der richtigen
    Schiffsart zu erzeugen. Somit braucht es kein eigenes Feld.
    
    Der JP Zuschlag des Sektionsfahren wird ebenfalls beim Speichern als eine
    'Bewertung' für die Gruppe gespeichert. Darum kein eigenes Feld.
    
    """
    chef = models.ForeignKey('Mitglied')
    sektion = models.ForeignKey('Sektion')
    name = models.CharField(max_length=20) # z.B. Bremgarten I


class Schiffsektion(Teilnehmer):
    """
    Ein Schiff im Sektionsfahren.
    
    Die Startnummer entspricht der Position 1,2,3,... innerhalb Gruppe, was bei
    der Noteneingabe wichtig ist. Dies bedeutet allerdings, dass die
    Startnummer nicht unique für eine Disziplin sein kann.
    """
    gruppe = models.ForeignKey('Gruppe')
    schiffsart = models.CharField(max_length=1, choices=SCHIFFS_ART)


class Schiffeinzel(Teilnehmer):
    """
    Ein Schiff im Einzelfahren.
    
    Doppelstarter werden automatisch bei Erstellung der Rangliste gesucht,
    entsprechend braucht es kein eigenes Feld.  Die Schiffsart wird von der
    Kategorie abgeleitet.
    """
    steuermann = models.ForeignKey('Mitglied', related_name='steuermann')
    vorderfahrer = models.ForeignKey('Mitglied', related_name='vorderfahrer')
    sektion = models.ForeignKey('Sektion')
    kategorie = models.ForeignKey('Kategorie')
    schiffsart = models.CharField(max_length=1, choices=SCHIFFS_ART)


# Hilfstabellen für Ranglisten

class Richtzeit(models.Model):
    """
    Zeit in Millisekunden, welche 10 Punkte auf dem Notenblatt ergeben.
    """
    posten = models.ForeignKey('Posten')
    zeit = models.DecimalField(max_digits=4, decimal_places=2)


class Kranzlimite(models.Model):
    """
    Anzahl Punkte oder die Zeit, mit der der letzte Kranz erreicht wird.
    """
    disziplin = models.ForeignKey('Disziplin')
    kategorie = models.ForeignKey('Kategorie')
    wert = models.DecimalField(max_digits=2, decimal_places=0)
