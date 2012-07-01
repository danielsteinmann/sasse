Frische Installation (Kurz)
--------------------
  mkdir c:\_tmp_sasse
  cd c:\_tmp_sasse
  unzip sasse-setup.zip
  cd sasse-setup
  installers/python-2.7.1.msi
  installers/reportlab-2.5.win32-py2.7.exe
  installers/postgresql-9.0.4-1-windows.exe
  installers/psycopg2-2.4.1.win32-py2.7-pg9.0.4-release.exe
  set Path=%Path%;c:\Python27;C:\Programme\PostgreSQL\9.0\bin
  # Diesen Pfad auch permanent setzen:
  #  Start->Einstellungen->Systemsteuerung->System->Erweiterungen->Umgebungsvariable
  rmdir /s c:\pythonenv
  rmdir /s c:\django
  python virtualenv.py --distribute --extra-search-dir=pypi C:\pythonenv\sasse
  c:\pythonenv\sasse\Scripts\activate.bat
  pip install -f file://%CD%/pypi -f file://%CD% sasse
  createdb -U postgres spsv                      #Passwort von PostgreSQL Installation
  psql -U postgres -d spsv -f spsv.pgdump
  unzip djangosites.zip -d c:\
  copy local_settings_example.py C:\djangosites\wettkaempfe
  cd C:\djangosites\wettkaempfe
  rename local_settings_example.py local_settings.py
  notepad local_settings.py                      #Passwort von PostgreSQL Installation
  rmdir /s c:\_tmp_sasse
  python manage.py runserver --noreload 0.0.0.0:8000

Frische Installation (Lang)
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
  Mit 'virtualenv.py' ein Python Environment erzeugen. Dazu eine Windows Shell
  öffnen und folgendes eintippen:
    cd SOME-TMP-DIR
    unzip sasse-setup.zip
    cd sasse-setup
    python virtualenv.py --distribute --extra-search-dir=pypi C:\pythonenv\sasse

- Python Software
  Mit folgenden Befehlen werden Sasse und all die davon abhängigen
  Softwarekomponenten in das Python Environment installiert:
    c:\pythonenv\sasse\Scripts\activate.bat
    pip install -f file://%CD%/pypi -f file://%CD% sasse

- Django Website
  Die Website ist mit Hilfe des Django Framework erzeugt worden. Folgendes
  ZIP File enthält Konfigurationsscripte, welche die Website für die SPSV
  Wettkämpfe definieren:
    unzip djangosites.zip -d c:\

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
    pip install -U --no-deps sasse-X.X.tar.gz
    python manage.py migrate


Webserver
---------
    cd c:\djangosites\wettkaempfe
    c:/pythonenv/sasse/Scripts/activate.bat
    python manage.py runserver --noreload 0.0.0.0:8000


Datenbank Export/Import
-----------------------
    pg_dump --clean -U postgres -f spsv.pgdump spsv   # Export
    psql -U postgres -d spsv -f spsv.pgdump           # Import
