Frische Installation
--------------------
- python-2.7.1.msi
  Alle Defaults wählen. Python wird in das Verzeichnis c:/python27 installiert.

- postgresql-9.0.4-1-windows.exe
  Alle Defaults wählen. Das Passwort muss man sich merken.  Den Stack Builder
  muss nicht gestartet werden.

- Umgebungsvariable PATH
  Python und PostgreSQL in den Pfad aufnehmen:
  - Start->Einstellungen->Systemsteuerung, dort 'System' auswählen
  - Auf Tab 'Erweiterungen' wechseln und Knopf 'Umgebungsvariablen' drücken
  - Im Bereich 'Systemvariablen' die Variable 'Path' auswählen
  - Knopf 'Bearbeiten' drücken und an Ende von 'Wert der Variablen' navigieren
  - Dort ';c:\Python27;C:\Programme\PostgreSQL\9.0\bin' eingeben und OK drücken

- psycopg2-2.4.1.win32-py2.7-pg9.0.4-release.exe
  Alle Defaults wählen. Muss die Binary Distribution nehmen, weil es DLLs
  enthält, die ohne Compiler nicht erzeugt werden können.

- reportlab-2.5.win32-py2.7.exe
  Alle Defaults wählen. Muss die Binary Distribution nehmen, weil es DLLs
  enthält, die ohne Compiler nicht erzeugt werden können.

- Python Environment
  Um nicht von einer Internet Verbindung abhängig zu sein, wird eine Kopie der
  relevanten Packages des Python Packaging Repostories (PyPI) mitgeliefert.
  Der Rest dieser Anleitung geht davon aus, dass diese Packages unter 'y:\pypi'
  erreichbar sind.
  Mit 'virtualenv.py' ein Python Environment erzeugen. Dazu eine Windows Shell
  öffnen und folgendes eintippen:
    python y:\virtualenv.py --extra-search-dir=y:\pypi C:\pythonenv\sasse

- Python Software
  Mit folgenden Befehlen werden Sasse und all die davon abhängigen
  Softwarekomponenten in das Python Environment installiert:
    c:\pythonenv\sasse\Scripts\activate.bat
    pip install -f file:y:\pypi sasse

  Das Package 'sasse' hängt von folgenden Packages ab:
  - Django-1.3.tar.gz
  - South-0.7.3.tar.gz
  - django-pagination-1.0.7.tar.gz
  - xlrd-0.7.1.zip

- Django Website
  Die Website ist mit Hilfe des Django Framework erzeugt worden. Folgendes
  ZIP File enthält Konfigurationsscripte, welche die Website für die SPSV
  Wettkämpfe definieren:
    unzip y:\djangosites.zip -d c:\

- Datenbank
  Mit folgenden Befehlen wird eine Datenbank Instanz erzeugt, die Tabellen
  erstellt und mit Initialdaten gefüllt:
    cd c:\djangosites\wettkaempfe
    createdb -U postgres spsv  #Passwort von PostgreSQL Installation
    python manage.py syncdb    #Admin User für Webapplikation eingeben
    python manage.py migrate
    python manage.py import_mitglieder_spsv EXCEL-FILE

  (Excel File mit 'qryExportWetkämpferfürDaniSteinmannNachAlt' erzeugen)


Upgrade
-------
    cd c:\djangosites\wettkaempfe
    c:\pythonenv\sasse\Scripts\activate.bat
    pip install -U --no-deps -f file:y:\ sasse
    python manage.py syncdb
    python manage.py migrate


Webserver
---------
    cd c:\djangosites\wettkaempfe
    c:/pythonenv/sasse/Scripts/activate.bat
    python manage.py runserver --noreload 0.0.0.0:8000


Datenbank Export/Import
-----------------------
    pg_dump -U postgres -f spsv.pgdump spsv   # Export
    psql -U postgres -d spsv -f spsv.pgdump   # Import
