Frische Installation
====================

Python (python-3.12.3-amd64.exe)
------
Selektiere "Add python.exe to PATH" und dann "Install Now".

PostgreSQL (postgresql-14.7-2-windows-x64.exe)
----------
Alle Defaults wählen. Das Admin Passwort sich gut merken. Den Stack Builder
muss nicht gestartet werden.

PostgreSQL in den Pfad aufnehmen:
- Start->Einstellungen->Systemsteuerung, dort 'System' auswählen
- Auf Tab 'Erweiterungen' wechseln und Knopf 'Umgebungsvariablen' drücken
- Im Bereich 'Systemvariablen' die Variable 'Path' auswählen
- Knopf 'Bearbeiten' drücken und an Ende von 'Wert der Variablen' navigieren
- Dort 'C:\Programme\PostgreSQL\14\bin' eingeben und OK drücken

DB erzeugen:

    createdb -U postgres spsv  # Admin Passwort von Installation

Web Applikation (djangosites.zip, sasse-3.0.0.tar.gz)
---------------
Die Web Applikation ist mit Hilfe des Python Framework Django geschrieben.

Die Basiskonfiguration wird wie folgt erzeugt:

    unzip "c:/Users/admin/Downloads/djangosites.zip" to "C:\"
    cd c:/djangosites/wettkaempfe

Nun das DB Passwort in `mysite/settings.py` entsprechend anpassen und dann
folgende Kommandi ausführen:

    python -m venv c:/pythonenv/sasse
    c:/pythonenv/sasse/Scripts/activate.bat
    pip install c:/Users/admin/Downloads/sasse-3.0.0.tar.gz
    pip install uvicorn
    pip install whitenoise
    python manage.py collectstatic
    python manage.py migrate
    python manage.py import_mitglieder_spsv EXCEL-FILE

Web Server (uvicorn)
----------
Der Web Server `uvicorn` wurde mit vorherigen Schritt schon installiert.

Damit der Web Server als Windows Service startet, das Tool
[shawl.exe](https://github.com/mtkennerly/shawl) herunterladen und den Service
wie folgt erzeugen (CMD als Administrator):

    copy c:/Users/admin/Downloads/shawl.exe c:/djangosites/wettkaempfe
    sc create sasse binPath="C:/djangosites/wettkaempfe/shawl.exe run --name sasse --cwd C:/djangosites/wettkaempfe -- C:/pythonenv/sasse/Scripts/uvicorn.exe --host 0.0.0.0 --port 80 mysite.asgi:application"
    sc config sasse start=auto
    sc start sasse


Mit folgenden Kommandi kann man den Web Server interaktiv starten:

    cd c:/djangosites/wettkaempfe
    c:/pythonenv/sasse/Scripts/activate.bat
    uvicorn mysite.asgi:application


Upgrade
=======

    cd c:\djangosites\wettkaempfe
    c:\pythonenv\sasse\Scripts\activate.bat
    pip install sasse-X.X.X.tar.gz
    python manage.py migrate
    python manage.py import_mitglieder_spsv EXCEL-FILE


Datenbank Export/Import
=======================

    pg_dump --clean -U postgres -f spsv.pgdump spsv   # Export
    psql -U postgres -d spsv -f spsv.pgdump           # Import


SAT Mitglieder Export
=====================

Mit folgenden Schritten das Excel erzeugen, welches mit
`import_mitglieder_spsv` eingelesen werden kann:

1. In https://www.sat.admin.ch auf Stufe SPSV einloggen
2. Auswertungen => Personen => Mitgliedschaftsliste
3. Im Excel folgende Spalten löschen:
    - `Firma` bis `Webseite`
    - `Verstorben` bis `Einteilung`
    - `Bemerkung`
4. Im Excel folgende Filter setzen:
    - `Datum bis` auf `blanks`
    - `Kategorie` auf `Aktiv`
5. Daten in neues Excel kopieren (nur Werte).
6. Für Spalte `Geburtsdatum` das Datum Format wählen
