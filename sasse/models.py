# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.urls import reverse
from .templatetags.sasse import zeit2str

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
    nummer = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Mitglied(models.Model):
    nummer = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=50)
    vorname = models.CharField(max_length=50)
    geburtsdatum = models.DateField()
    geschlecht = models.CharField(max_length=1, choices=GESCHLECHT_ART)
    sektion = models.ForeignKey('Sektion', on_delete=models.CASCADE)

    class Meta:
        ordering = ['name', 'vorname', 'sektion']

    def __str__(self):
        return '%s %s, %d, %s' % (self.name, self.vorname, self.geburtsdatum.year, self.sektion)


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

    def __str__(self):
        return self.name


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

    def __str__(self):
        return self.name


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
    postenart = models.ForeignKey('Postenart', on_delete=models.CASCADE)
    gruppe = models.CharField(max_length=6, choices=GRUPPE_TYP, default="ZIEL")
    name = models.CharField(max_length=50)
    signum = models.SmallIntegerField(default=1)
    einheit = models.CharField(max_length=6, choices=EINHEIT_TYP)
    defaultwert = models.DecimalField(max_digits=6, decimal_places=1)
    wertebereich = models.CharField(max_length=200)
    reihenfolge = models.SmallIntegerField(default=1) # Was kommt auf GUI zuerst
    editierbar = models.BooleanField(default=True) # Erscheint es auf dem GUI

    class Meta:
        ordering = ['postenart', 'reihenfolge']

    def __str__(self):
        return '%s, %s' % (self.postenart.name, self.name)


class Kategorie(models.Model):
    disziplinart = models.ForeignKey('Disziplinart', on_delete=models.CASCADE)
    name = models.CharField(max_length=10)
    alter_von = models.PositiveSmallIntegerField()
    alter_bis = models.PositiveSmallIntegerField()
    reihenfolge = models.SmallIntegerField(default=1) # Was kommt auf GUI zuerst

    class Meta:
        ordering = ['reihenfolge']

    def __str__(self):
        return self.name


# Bewegungsdaten


class Wettkampf(models.Model):
    name = models.CharField(max_length=50, unique_for_year='von')
    zusatz = models.CharField(max_length=100)
    von = models.DateField(help_text="Format: JJJJ-MM-DD")
    bis = models.DateField(null=True, blank=True, help_text="(optional)")
    JPSM = models.BooleanField(default=False, help_text="Ist es eine JP SM? Hat Einfluss auf die Kategoriewahl bei der Startliste")

    class Meta:
        ordering = ['-von']

    def __str__(self):
        return self.name

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
    wettkampf = models.ForeignKey('Wettkampf', on_delete=models.CASCADE)
    name = models.SlugField(allow_unicode=True, max_length=50)
    disziplinart = models.ForeignKey('Disziplinart', on_delete=models.CASCADE, blank=False, default=1)
    kategorien = models.ManyToManyField('Kategorie', blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        if self.disziplinart.name == "Sektionsfahren":
            return reverse('sektionsfahren_get', args=[str(self.wettkampf.jahr()), self.wettkampf.name])
        elif self.disziplinart.name == "Schwimmen":
            return reverse('schwimmen_get', args=[str(self.wettkampf.jahr()), self.wettkampf.name])
        elif self.disziplinart.name == "Einzelschnüren":
            return reverse('einzelschnueren_get', args=[str(self.wettkampf.jahr()), self.wettkampf.name])
        elif self.disziplinart.name == "Gruppenschnüren":
            return reverse('gruppenschnueren_get', args=[str(self.wettkampf.jahr()), self.wettkampf.name])
        elif self.disziplinart.name == "Bootsfährenbau":
            return reverse('bootfaehrenbau_get', args=[str(self.wettkampf.jahr()), self.wettkampf.name])
        else:
            return reverse('disziplin_get', args=[str(self.wettkampf.jahr()), self.wettkampf.name, self.name])

    def get_base_template(self):
        art = self.disziplinart.name
        if art == "Einzelfahren":
            return "base_disziplin.html"
        elif art == "Sektionsfahren":
            return "base_sektionsfahren.html"
        elif art == "Schwimmen":
            return "base_schwimmen.html"
        elif art == "Einzelschnüren":
            return "base_einzelschnueren.html"
        elif art == "Gruppenschnüren":
            return "base_gruppenschnueren.html"
        elif art == "Bootsfährenbau":
            return "base_bootfaehrenbau.html"
        else:
            return None

    class Meta:
        unique_together = ['wettkampf', 'name']
        ordering = ['name']


class Posten(models.Model):
    disziplin = models.ForeignKey('Disziplin', on_delete=models.CASCADE)
    name = models.CharField(max_length=10)
    postenart = models.ForeignKey('Postenart', on_delete=models.CASCADE)
    reihenfolge = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ['disziplin', 'name']
        ordering = ['reihenfolge', 'name']


class Bewertung(models.Model):
    """
    Wert ist entweder Anzahl Punkte oder Zeit in Hundertstel Sekunden.
    """
    teilnehmer = models.ForeignKey('Teilnehmer', on_delete=models.CASCADE)
    posten = models.ForeignKey('Posten', on_delete=models.CASCADE)
    bewertungsart = models.ForeignKey('Bewertungsart', on_delete=models.CASCADE)
    note = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    zeit = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    class Meta:
        unique_together = ('teilnehmer', 'posten', 'bewertungsart')

    def __str__(self):
        if self.bewertungsart.einheit == 'ZEIT':
            wert = self.zeit
            return '%s' % (zeit2str(wert),)
        else:
            wert = self.note
            if wert == 0:
                return '0'
            return '%.1f' % (wert,)


class Teilnehmer(models.Model):
    """
    Die gemeinsamen Attribute für einen Teilnehmer an einem Wettkampf.
    """
    disziplin = models.ForeignKey('Disziplin', on_delete=models.CASCADE)
    startnummer = models.PositiveIntegerField()
    disqualifiziert = models.BooleanField(default=False)
    ausgeschieden = models.BooleanField(default=False)

    def __str__(self):
        return '%d' % (self.startnummer,)

    class Meta:
        unique_together = ('disziplin', 'startnummer')
        ordering = ['startnummer']


class Person(Teilnehmer):
    """
    Ein Schwimmer oder Schnürer.
    """
    mitglied = models.ForeignKey('Mitglied', on_delete=models.CASCADE)
    sektion = models.ForeignKey('Sektion', on_delete=models.CASCADE)
    kategorie = models.ForeignKey('Kategorie', on_delete=models.CASCADE)


class Schwimmer(Teilnehmer):
    mitglied = models.ForeignKey('Mitglied', on_delete=models.CASCADE)
    kategorie = models.CharField(max_length=10)
    zeit = models.DecimalField(max_digits=6, decimal_places=2)
    creation_date = models.DateTimeField(auto_now_add=True)

    def save(self):
        self.kategorie = self._get_kategorie()
        super(Schwimmer, self).save()

    def _get_kategorie(self):
        aktuelles_jahr = self.disziplin.wettkampf.jahr()
        geburts_jahr = self.mitglied.geburtsdatum.year
        alter = aktuelles_jahr - geburts_jahr
        if alter <= 14:
            return "I"
        elif self.mitglied.geschlecht == "f":
            return "F"
        elif alter <= 17:
            return "II"
        elif alter <= 20:
            return "III"
        elif alter <= 42:
            return "C"
        else:
            return "D"

class Einzelschnuerer(Teilnehmer):
    mitglied = models.ForeignKey('Mitglied', on_delete=models.CASCADE)
    kategorie = models.CharField(max_length=10)
    parcourszeit = models.DecimalField(max_digits=6, decimal_places=2)
    zuschlaege = models.DecimalField(max_digits=6, decimal_places=2)
    zeit = models.DecimalField(max_digits=6, decimal_places=2)
    creation_date = models.DateTimeField(auto_now_add=True)

    def save(self):
        self.kategorie = self._get_kategorie()
        self.zeit = self.parcourszeit + self.zuschlaege
        super(Einzelschnuerer, self).save()

    def _get_kategorie(self):
        aktuelles_jahr = self.disziplin.wettkampf.jahr()
        geburts_jahr = self.mitglied.geburtsdatum.year
        alter = aktuelles_jahr - geburts_jahr
        if alter <= 14:
            return "I"
        elif self.mitglied.geschlecht == "f":
            return "F"
        elif alter <= 17:
            return "II"
        elif alter <= 20:
            return "III"
        elif alter <= 42:
            return "C"
        else:
            return "D"

class Schnuergruppe(Teilnehmer):
    KATEGORIE = (
            ('JP', 'JP'),
            ('Aktive', 'Aktive'),
            )
    sektion = models.ForeignKey('Sektion', on_delete=models.CASCADE)
    name = models.CharField(max_length=20) # z.B. Bremgarten I
    kategorie = models.CharField(max_length=10, choices=KATEGORIE, default="Aktive")
    aufbauzeit = models.DecimalField(max_digits=6, decimal_places=2)
    abbauzeit = models.DecimalField(max_digits=6, decimal_places=2)
    zuschlaege = models.DecimalField(max_digits=6, decimal_places=1)
    zeit = models.DecimalField(max_digits=6, decimal_places=2)
    creation_date = models.DateTimeField(auto_now_add=True)

    def save(self):
        self.zeit = self.aufbauzeit + self.abbauzeit + self.zuschlaege
        super(Schnuergruppe, self).save()

class Bootfaehrengruppe(Teilnehmer):
    sektion = models.ForeignKey('Sektion', on_delete=models.CASCADE)
    name = models.CharField(max_length=20) # z.B. Bremgarten I
    kategorie = models.CharField(max_length=10, default="Aktive")
    zuschlaege = models.DecimalField(max_digits=6, decimal_places=1)
    einbauzeit = models.DecimalField(max_digits=6, decimal_places=2)
    ausbauzeit = models.DecimalField(max_digits=6, decimal_places=2)
    zeit = models.DecimalField(max_digits=6, decimal_places=2)
    creation_date = models.DateTimeField(auto_now_add=True)

    def save(self):
        self.zeit = self.einbauzeit + self.ausbauzeit + self.zuschlaege
        super(Bootfaehrengruppe, self).save()

class SektionsfahrenGruppeManager(models.Manager):
    def with_counts(self, disziplin):
        from .queries import read_sektionsfahren_gruppen_counts
        counts = read_sektionsfahren_gruppen_counts(disziplin)
        result_list = []
        for p in self.get_queryset().select_related().filter(disziplin=disziplin).order_by('startnummer'):
            p._set_counts(counts)
            result_list.append(p)
        return result_list

class Sektionsfahrengruppe(Teilnehmer):
    """
    Eine Schnürgruppe, eine Bootfährenbautrupp oder eine Sektion beim
    Sektionsfahren.
    """
    chef = models.ForeignKey('Mitglied', on_delete=models.CASCADE)
    sektion = models.ForeignKey('Sektion', on_delete=models.CASCADE)
    name = models.CharField(max_length=20) # z.B. Bremgarten I
    abzug_gruppe = models.DecimalField(max_digits=6, decimal_places=1, default=0, blank=True)
    abzug_sektion = models.DecimalField(max_digits=6, decimal_places=1, default=0, blank=True)
    abzug_gruppe_comment = models.CharField(null=True, blank=True, max_length=400)
    abzug_sektion_comment = models.CharField(null=True, blank=True, max_length=400)
    objects = SektionsfahrenGruppeManager()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def schiffe(self):
        return Schiffsektion.objects.select_related().filter(gruppe=self.id)

    def _set_counts(self, counts=None):
        if counts is None:
            from .queries import read_sektionsfahren_gruppen_counts
            counts = read_sektionsfahren_gruppen_counts(self.disziplin, self)
        anz_schiffe, anz_jps, anz_frauen, anz_senioren = counts
        grp = self.name
        self._anz_schiffe = anz_schiffe[grp]
        self._anz_jps = anz_jps[grp]
        self._anz_frauen = anz_frauen[grp]
        self._anz_senioren = anz_senioren[grp]

    def anz_schiffe(self):
        if not hasattr(self, '_anz_schiffe'):
            self._set_counts()
        return self._anz_schiffe

    def anz_jps(self):
        if not hasattr(self, '_anz_jps'):
            self._set_counts()
        return self._anz_jps

    def anz_frauen(self):
        if not hasattr(self, '_anz_frauen'):
            self._set_counts()
        return self._anz_frauen

    def anz_senioren(self):
        if not hasattr(self, '_anz_senioren'):
            self._set_counts()
        return self._anz_senioren


class Schiffsektion(Teilnehmer):
    """
    Ein Schiff im Sektionsfahren.
    
    Position 1, 2, etc innerhalb der Gruppe ist bei der Noteneingabe wichtig.
    """
    gruppe = models.ForeignKey('Sektionsfahrengruppe', on_delete=models.CASCADE)
    position = models.PositiveSmallIntegerField()
    ft1_steuermann = models.ForeignKey('Mitglied', on_delete=models.CASCADE, related_name='ft1_steuermann')
    ft1_vorderfahrer = models.ForeignKey('Mitglied', on_delete=models.CASCADE, related_name='ft1_vorderfahrer')
    ft2_steuermann = models.ForeignKey('Mitglied', on_delete=models.CASCADE, related_name='ft2_steuermann')
    ft2_vorderfahrer = models.ForeignKey('Mitglied', on_delete=models.CASCADE, related_name='ft2_vorderfahrer')

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
    steuermann = models.ForeignKey('Mitglied', on_delete=models.CASCADE, related_name='steuermann')
    vorderfahrer = models.ForeignKey('Mitglied', on_delete=models.CASCADE, related_name='vorderfahrer')
    steuermann_ist_ds = models.BooleanField(default=False)
    vorderfahrer_ist_ds = models.BooleanField(default=False)
    sektion = models.ForeignKey('Sektion', on_delete=models.CASCADE)
    kategorie = models.ForeignKey('Kategorie', on_delete=models.CASCADE)
    # Schiffsart lässt sich aus der Kategorie ableiten, darum nicht erfasst

    def steuermann_kat(self):
      jahr = self.disziplin.wettkampf.jahr()
      return self.calc_kategorie(jahr, self.steuermann)

    def vorderfahrer_kat(self):
      jahr = self.disziplin.wettkampf.jahr()
      return self.calc_kategorie(jahr, self.vorderfahrer)

    def calc_kategorie(self, aktuelles_jahr, mitglied):
        alter = aktuelles_jahr - mitglied.geburtsdatum.year
        return Kategorie.objects.exclude(name__in=["FII","FIII","F"]).filter(
                Q(alter_von__lte=alter),
                Q(alter_bis__gte=alter)
                )[0]

    def calc_startkategorie(self):
        """
        Frauen werden kategoriemässig als Mann behandelt, wenn sie mit einem Mann
        zusammen starten. Beispiele:
        - Frau-15 mit Mann-15 => Kat II
        - Frau-19 mit Mann-18 => Kat III
        - Frau-23 mit Mann-45 => Kat C

        Zudem gibt es an den JP Schweizermeisterschafen keine Kategorie F:
        - Frau-15 mit Frau-16 => Kat FII
        - Frau-19 mit Frau-18 => Kat FIII
        - Frau-23 => Darf nicht starten
        """
        jpsm = self.disziplin.wettkampf.JPSM
        hinten_kat = self.steuermann_kat()
        vorne_kat = self.vorderfahrer_kat()
        kat = {}
        for k in Kategorie.objects.all():
            kat[k.name] = k
        kat_I = kat["I"]
        kat_II = kat["II"]
        kat_III = kat["III"]
        kat_C = kat["C"]
        kat_D = kat["D"]
        kat_FII = kat["FII"]
        kat_FIII = kat["FIII"]
        kat_F = kat["F"]
        if jpsm:
            # An der JP SM duerfen nur JPs (max 20. Altersjahr) starten
            for k in [hinten_kat, vorne_kat]:
                if k not in [kat_I, kat_II, kat_III]:
                    return None
        if self.steuermann.geschlecht == "f" and self.vorderfahrer.geschlecht == "f":
            # Reines Frauenpaar
            if hinten_kat == kat_I and vorne_kat == kat_I:
                return kat_I
            if hinten_kat in (kat_I, kat_II) and vorne_kat in (kat_I, kat_II):
                return kat_FII
            if hinten_kat in (kat_I, kat_II, kat_III) and vorne_kat in (kat_I, kat_II, kat_III):
                return kat_FIII
            if hinten_kat in (kat_II, kat_III, kat_C, kat_D) and vorne_kat in (kat_II, kat_III, kat_C, kat_D):
                return kat_F
            return None
        if hinten_kat == vorne_kat:
            return hinten_kat
        if hinten_kat in (kat_I, kat_II) and vorne_kat in (kat_I, kat_II):
            return kat_II
        if hinten_kat in (kat_I, kat_II, kat_III) and vorne_kat in (kat_I, kat_II, kat_III):
            return kat_III
        if hinten_kat in (kat_II, kat_III, kat_C, kat_D) and vorne_kat in (kat_II, kat_III, kat_C, kat_D):
            return kat_C
        return None


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
    posten = models.ForeignKey('Posten', on_delete=models.CASCADE)
    zeit = models.DecimalField(max_digits=6, decimal_places=2)


class Kranzlimite(models.Model):
    """
    Anzahl Punkte oder die Zeit, mit der der letzte Kranz erreicht wird.
    """
    disziplin = models.ForeignKey('Disziplin', on_delete=models.CASCADE)
    kategorie = models.ForeignKey('Kategorie', on_delete=models.CASCADE)
    wert = models.DecimalField(max_digits=6, decimal_places=1)

    def __str__(self):
        return '%s, %s, %d' % (self.disziplin, self.kategorie, self.wert)


class SpezialwettkaempfeKranzlimite(models.Model):
    disziplin = models.ForeignKey('Disziplin', on_delete=models.CASCADE)
    kategorie = models.CharField(max_length=10)
    zeit = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return '%s, %s, %d' % (self.disziplin, self.kategorie, self.zeit)


class SektionsfahrenKranzlimiten(models.Model):
    disziplin = models.ForeignKey('Disziplin', on_delete=models.CASCADE)
    gold = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    silber = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    lorbeer = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    ausser_konkurrenz = models.ForeignKey('Sektion', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.disziplin


class SektionsfahrenZeitimport(models.Model):
    schiffsektion = models.ForeignKey('Schiffsektion', on_delete=models.CASCADE)
    posten = models.ForeignKey('Posten', on_delete=models.CASCADE)
    startnummer_calc = models.PositiveIntegerField()

    def __str__(self):
        return self.startnummer_calc

    class Meta:
        unique_together = ['posten', 'schiffsektion', 'startnummer_calc']
