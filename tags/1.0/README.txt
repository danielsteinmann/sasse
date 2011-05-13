Frische Installation
--------------------
- PyPI
  Da nicht von einer Internet Verbindung ausgangen werden kann, wird eine Kopie
  der relevanten Packages des Python Packaging Repostories (PyPI) mitgeliefert. 
  Der Rest dieser Anleitung geht davon aus, dass diese Packages unter 'y:\pypi'
  erreichbar sind.

- Installation von python-2.7.1.msi
  Python wird in das Verzeichnis c:/python27 installiert.

- Installation von reportlab-2.5.win32-py2.7.exe
  Muss die Binary Distribution nehmen, weil es DLLs enthält, die ohne Compiler
  nicht erzeugt werden können.

- Python Environment
  Mit 'virtualenv.py' ein Python Environment erzeugen. Dazu eine Windows Shell
  öffnen und folgendes eintippen:
    c:\Python27\python.exe y:\pypi\virtualenv.py --distribute --extra-search-dir=y:\pypi C:\pythonenv\sasse

  HINWEIS: Da die ReportLab Packages werden in die Python-2.7 'site-packages'
  installiert werden, darf der Parameter 'no-site-packages' von 'virtualenv'
  nicht verwendet werden.

- Sasse Software
  Mit 'pip', das durch vorherigen Schritt installiert wurde, kann Sasse und all
  die davon abhängigen Softwarekomponenten in das Python Environment
  installiert werden:
    c:/pythonenv/sasse/Scripts/activate.bat
    pip install -f file:y:\pypi sasse

- Django Website konfigurieren
  Ein Verzeichnis 'c:\django' anlegen und dorthinein das Verzeichnis
  'wettkampf' kopieren. Dies sind Scripte, welche eine Website basierend auf
  dem Django Framework definieren.

- Datenbank aufsetzen
  Nun muss die Datenbank erzeugt werden und die Mitgliederdaten importiert
  werden:
    cd c:\django\wettkampf
    python manage.py syncdb    #Bei leerer DB neuen Admin User eingeben
    python manage.py migrate
    python manage.py import_mitglieder_spsv EXCEL-FILE

- Webserver starten
  Zu guter letzt den Webserver starten:
    python manage.py runserver 0.0.0.0:8000


Upgrade
-------
- Software/Datenbank aktualisieren
    c:/pythonenv/sasse/Scripts/activate.bat
    pip install -f file:y:\pypi sasse
    cd c:\django\wettkampf
    python manage.py syncdb
    python manage.py migrate

- Webserver starten
    python manage.py runserver 0.0.0.0:8000
