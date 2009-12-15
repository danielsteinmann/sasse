# -*- coding: utf-8 -*-

from django.db.models.signals import post_syncdb
from django.template.loader import render_to_string

from sasse import models as sasse_app


def install_views(sender, **kwargs):
    from django.db import connection
    print "Installing view 'bewertung_in_punkte'"
    cursor = connection.cursor()
    try:
        cursor.execute("drop view bewertung_in_punkte")
    except:
        pass # View existiert noch nicht
    sql = render_to_string('bewertung_in_punkte.sql')
    cursor.execute(sql)


post_syncdb.connect(install_views, sender=sasse_app)
