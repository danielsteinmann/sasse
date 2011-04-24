# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from templatetags.sasse import zeit2str

# Die Permissions werden erst in einem post_sync Schritt von Django gemacht.
# Das passiert erst, *nachdem* die South-Migrations installiert werden. Wenn
# nun eine Migration auf solche Permissions zugreifen möchte, dann müssen diese
# vorhanden sein.
# Siehe http://south.aeracode.org/ticket/211
if 'django.contrib.auth' in settings.INSTALLED_APPS:
    from south.signals import pre_migrate
    def create_permissions_compat(app, **kwargs):
        from django.db.models import get_app
        from django.contrib.auth.management import create_permissions
        create_permissions(get_app(app), (), 0)
    pre_migrate.connect(create_permissions_compat)

SCHIFFS_ART = (
        ('b', 'Boot'),
        ('w', 'Weidling'),
        )

GESCHLECHT_ART = [
        ('f', 'Frau'),
        ('m', 'Mann'),
        ]

# Stammdaten (importiert)

class Sektion(models.Model):
    nummer = models.CharField(max_length=2, unique=True)
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return u'%s' % (self.name,)


class Mitglied(models.Model):
    nummer = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=50)
    vorname = models.CharField(max_length=50)
    geburtsdatum = models.DateField()
    geschlecht = models.CharField(max_length=1, choices=GESCHLECHT_ART)
    sektion = models.ForeignKey('Sektion')

    class Meta:
        ordering = ['name', 'vorname', 'sektion']

    def __unicode__(self):
        return u'%s %s, %d, %s' % (self.name, self.vorname, self.geburtsdatum.year, self.sektion)


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

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return u'%s' % (self.name,)


class Bewertungsart(models.Model):
    """
    Beispiel: Abfahrt an einer Stange

       Gruppe Name        Punkte
       ------ ----------- ------
       Ziel   Distanznote    9.5 positiv           (Lappen knapp nicht)
       Stil   Maximum       10.0 positiv, non-edit 
       Stil   Anprallen     -2.0 negativ           (Abzug) 
       Stil   Kommando      -1.0 negativ           (Abzug)
                          ------
                            16.5

    Ergibt folgendes Notenblatt:

       Posten  Uebungsteil               Abzug   Note   Zeit Total
       ------  ------------------------ ------ ------ ------ -----
       C       Abfahrt bei einer Stange    3.0    9.5         16.5
    """
    GRUPPE_TYP = (
            ('ZIEL', 'Ziel'),
            ('STIL', 'Stil'),
            )
    EINHEIT_TYP = (
            ('PUNKT', 'Punkte'),
            ('ZEIT', 'Zeit'),
            )
    postenart = models.ForeignKey('Postenart')
    gruppe = models.CharField(max_length=6, choices=GRUPPE_TYP, default="ZIEL")
    name = models.CharField(max_length=50)
    signum = models.SmallIntegerField(default=1)
    einheit = models.CharField(max_length=6, choices=EINHEIT_TYP)
    defaultwert = models.DecimalField(max_digits=6, decimal_places=2)
    wertebereich = models.CharField(max_length=200)
    reihenfolge = models.SmallIntegerField(default=1) # Was kommt auf GUI zuerst
    editierbar = models.BooleanField(default=True) # Erscheint es auf dem GUI

    class Meta:
        ordering = ['postenart', 'reihenfolge']

    def __unicode__(self):
        return u'%s, %s' % (self.postenart.name, self.name)


class Kategorie(models.Model):
    disziplinart = models.ForeignKey('Disziplinart')
    name = models.CharField(max_length=10)
    alter_von = models.PositiveSmallIntegerField()
    alter_bis = models.PositiveSmallIntegerField()
    geschlecht = models.CharField(max_length=1, choices=GESCHLECHT_ART + [('e', 'egal')])
    reihenfolge = models.SmallIntegerField(default=1) # Was kommt auf GUI zuerst

    class Meta:
        ordering = ['reihenfolge']

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

    def __unicode__(self):
        return u'%s' % (self.name,)

    class Meta:
        unique_together = ['disziplin', 'name']
        ordering = ['reihenfolge', 'name']


class Bewertung(models.Model):
    """
    Wert ist entweder Anzahl Punkte oder Zeit in Hundertstel Sekunden.
    """
    teilnehmer = models.ForeignKey('Teilnehmer')
    posten = models.ForeignKey('Posten')
    bewertungsart = models.ForeignKey('Bewertungsart')
    note = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    zeit = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    class Meta:
        unique_together = ('teilnehmer', 'posten', 'bewertungsart')

    def __unicode__(self):
        if self.bewertungsart.einheit == 'ZEIT':
            wert = self.zeit
            return u'%s' % (zeit2str(wert),)
        else:
            wert = self.note
            if wert == 0:
                return u'0'
            return u'%.1f' % (wert,)


class Teilnehmer(models.Model):
    """
    Die gemeinsamen Attribute für einen Teilnehmer an einem Wettkampf.
    """
    disziplin = models.ForeignKey('Disziplin')
    startnummer = models.PositiveIntegerField()
    disqualifiziert = models.BooleanField(default=False)
    ausgeschieden = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%d' % (self.startnummer,)

    class Meta:
        unique_together = ('disziplin', 'startnummer')
        ordering = ['startnummer']


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
    
    Position 1, 2, etc innerhalb der Gruppe ist bei der Noteneingabe wichtig.
    """
    gruppe = models.ForeignKey('Gruppe')
    position = models.PositiveSmallIntegerField()
    schiffsart = models.CharField(max_length=1, choices=SCHIFFS_ART)

    class Meta:
        unique_together = ['gruppe', 'position']
        ordering = ['gruppe', 'position']


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
    # Schiffsart lässt sich aus der Kategorie ableiten, darum nicht erfasst


# Hilfstabellen für Ranglisten

class Richtzeit(models.Model):
    """
    Zeit in Sekunden, welche 10 Punkte auf dem Notenblatt ergeben.
    
    Zweimal Richtzeit = 0:
      0s   = 20 Punkte
      50s  = 15 Punkte
      100s = 10 Punkte
      150s = 5 Punkte
      200s = 0 Punkte     ==> 20 - (Zeit / (Richtzeit / 10))

    Dreimal Richtzeit = 0:
      0s   = 15 Punkte
      100s = 10 Punkte
      200s = 5 Punkte
      300s = 0 Punkte     ==> 15 - (Zeit / (Richtzeit / 5))
    """
    posten = models.ForeignKey('Posten')
    zeit = models.DecimalField(max_digits=6, decimal_places=2)


class Kranzlimite(models.Model):
    """
    Anzahl Punkte oder die Zeit, mit der der letzte Kranz erreicht wird.
    """
    disziplin = models.ForeignKey('Disziplin')
    kategorie = models.ForeignKey('Kategorie')
    wert = models.DecimalField(max_digits=6, decimal_places=2)

    def __unicode__(self):
        return u'%s, %s, %d' % (self.disziplin, self.kategorie, self.wert)

