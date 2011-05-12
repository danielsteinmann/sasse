# Müssen Absolut sein!
PKGS_DIR=$HOME/sasse/pkgs
ENV_DIR=$HOME/sasse-env

# Python Installieren
$PKGS_DIR/python-2.7.1.msi

# Sasse installieren
python $PKGS_DIR/virtualenv.py --distribute --no-site-packages --extra-search-dir=$PKGS_DIR $ENV_DIR
source $ENV_DIR/bin/activate
pip install -f file:$PKGS_DIR sasse

# Database install/upgrade
python manage.py syncdb    # (Bei leerer DB neuen Admin User eingeben)
python manage.py migrate

# Mitgliederdaten importieren/aktualisieren
python manage.py import_mitglieder_spsv EXCEL-FILE

# Webserver starten
python manage.py runserver 0.0.0.0:80 


Directories:
- C:/PYTHON27
- C:/SASSE_SOFTWARE/.../site-packages/
  reportlab/
  django/
  pagination/
  south/
  sasse/
- C:/SASSE_SERVER/
  __init__.py
  settings.py
  manage.py
  urls.py
  sasse_db.sqlite
