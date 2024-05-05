Frische Installation
--------------------
- sasse-setup-2023.zip
  Enthält die nachfolgend referenzierten Software Packages. Kann man z.B. auf
  dem Desktop auspacken.

- vcredist_x64.exe
  Microsft Visual C++ 2010 x64 Redistributable Setup installieren, damit alter
  Apache24 inklusive mod_wsgi noch läuft

- httpd-2.4.9-win64.zip
  Ordner 'Apache24' nach 'c:/' auspacken
  Adminstrationskonsole starten, 'c:/Apache24/bin/httpd -k install' ausführen

- mod_wsgi-3.4.ap24.win-amd64-py2.7.zip
  File 'mod_wsgi.so' nach c:/Apache24/modules auspacken

- python-2.7.16.amd64.msi
  Alle Defaults wählen. Python wird in das Verzeichnis c:/python27 installiert.

- postgresql-14.7-2-windows-x64.exe
  Alle Defaults wählen. Das Passwort 'spsv' vergeben. Falls ein anderes gewählt wird,
  unbedingt gut merken. Den Stack Builder muss nicht gestartet werden.

- Umgebungsvariable PATH
  Python und PostgreSQL in den Pfad aufnehmen:
  - Start->Einstellungen->Systemsteuerung, dort 'System' auswählen
  - Auf Tab 'Erweiterungen' wechseln und Knopf 'Umgebungsvariablen' drücken
  - Im Bereich 'Systemvariablen' die Variable 'Path' auswählen
  - Knopf 'Bearbeiten' drücken und an Ende von 'Wert der Variablen' navigieren
  - Dort ';c:\Python27;C:\Programme\PostgreSQL\14\bin' eingeben und OK drücken

- Python Environment
  Es wird ein Virtuelles Environment für Sasse eingerichtet, das die DLLs von
  ReportLab und PostgreSQL installiert sowie Sasse mit ihren Dependencies
  (automatisch vom Internet runtergeladen). Dafür eine Console starten und
  folgendes eingeben:
    cd <DESKTOP>/sasse-setup-2023
    python -m pip install --upgrade pip
    python -m pip install virtualenv
    python -m virtualenv c:\pythonenv\sasse
    c:\pythonenv\sasse\Scripts\activate.bat
    easy_install ./reportlab-2.5.win-amd64-py2.7.exe
    pip install psycopg2-binary  (installs 2.8.6)
    pip install ./sasse-2.12.tar.gz

- Django Website
  Die Website ist mit Hilfe des Django Framework erzeugt worden. Folgendes
  ZIP File enthält Konfigurationsscripte, welche die Website für die SPSV
  Wettkämpfe definieren:
    unzip djangosites.zip -d c:\
  HINWEIS: Falls ein anderes Passwort als 'spsv' für die PostgreSQL Datenbank
  vergeben wurde, muss man settings.py entsprechend anpassen.

- Apache Web Server
  Das Konfigurationsfile c:/Apache24/conf/httpd.conf wie folgt erweitern:
    LoadModule wsgi_module modules/mod_wsgi.so
    Include "c:/djangosites/wettkaempfe/httpd.conf"
  Nun über den Task Manager den 'Apache2.4' Service neu starten

- Django Development Web Server
  Falls man mit dem Apache Web Server nicht zurecht kommt, kann man den
  Django Development Web Server wie folgt verwenden
    cd c:\djangosites\wettkaempfe
    c:/pythonenv/sasse/Scripts/activate.bat
    python manage.py runserver --noreload 0.0.0.0:8000

- Datenbank
  Mit folgenden Befehlen wird eine Datenbank Instanz erzeugt, die Tabellen
  erstellt und mit Initialdaten gefüllt:
    cd c:\djangosites\wettkaempfe
    createdb -U postgres spsv  #Passwort von PostgreSQL Installation
    python manage.py syncdb    #Admin User für Webapplikation eingeben
    python manage.py migrate
    python manage.py import_mitglieder_spsv EXCEL-FILE

  (Excel mit 'qryExportWetkämpferfürDaniSteinmannNachAlt' als '.xls' erzeugen)


Upgrade
-------
    cd c:\djangosites\wettkaempfe
    c:\pythonenv\sasse\Scripts\activate.bat
    pip install -U --no-deps sasse-X.X.tar.gz
    python manage.py migrate

Datenbank Export/Import
-----------------------
    pg_dump --clean -U postgres -f spsv.pgdump spsv   # Export
    psql -U postgres -d spsv -f spsv.pgdump           # Import
