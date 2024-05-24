#/bin/bash
#
# Migrate to Django 5
#

dropdb spsv
createdb spsv
psql -U postgres -d spsv -f ../dumps/2023-09-10-dietikon-7er-cup.pgdump

psql -U postgres -d spsv <<EOF
alter table sasse_gruppe rename to sasse_sektionsfahrengruppe;
drop table auth_group cascade;
drop table auth_group_permissions cascade;
drop table auth_message cascade;
drop table auth_permission cascade;
drop table auth_user cascade;
drop table auth_user_groups cascade;
drop table auth_user_user_permissions cascade;
drop table django_admin_log cascade;
drop table django_content_type cascade;
drop table django_session cascade;
drop table django_site cascade;
drop table south_migrationhistory cascade;
EOF

./manage.py migrate --fake sasse 0002_rename_gruppe_sektionsfahrengruppe_and_more
./manage.py migrate

./manage.py shell <<EOF
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from sasse.models import Teilnehmer

rechnungsbuero = Group.objects.create(name='Rechnungsbüro')

# With Django 5 migration we had to rename 'Gruppe' to 'Sektionsfahrengruppe'.
# To minimize changes in views.py, we add manually the permissions here
ct = ContentType.objects.get_for_model(Teilnehmer)
Permission.objects.create(codename='add_gruppe', name='Can add Gruppe', content_type=ct)
Permission.objects.create(codename='change_gruppe', name='Can change Gruppe', content_type=ct)
Permission.objects.create(codename='delete_gruppe', name='Can delete Gruppe', content_type=ct)

PERMISSIONS = [
  'add_bewertung',
  'add_gruppe',
  'add_mitglied',
  'add_schiffeinzel',
  'add_schiffsektion',
  'change_bewertung',
  'change_gruppe',
  'change_mitglied',
  'change_schiffeinzel',
  'change_schiffsektion',
  'delete_bewertung',
  'delete_gruppe',
  'delete_mitglied',
  'delete_schiffeinzel',
  'delete_schiffsektion',
  'view_user',
]
for permission_code in PERMISSIONS:
  perm = Permission.objects.get(codename=permission_code)
  rechnungsbuero.permissions.add(perm)

user = User.objects.create_user("Noten", "rechnungsbuero@pontonier.ch", "teh-tarik")
user.is_staff = True
user.groups.add(rechnungsbuero)
user.save()
EOF

./manage.py createsuperuser --username=spsv --email=rechnungsbuero@pontonier.ch

./manage.py changepassword Noten
