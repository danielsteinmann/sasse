# -*- coding: utf-8 -*-

from django.db.models.signals import post_syncdb
from django.template.loader import render_to_string

from sasse import models as sasse_app


def install_views(sender, **kwargs):
    from django.db import connection
    cursor = connection.cursor()
    for view in ['bewertung_in_punkte', 'doppelstarter']:
        print "Installing view '%s'" % view
        try:
            cursor.execute("drop view %s" % view)
        except:
            pass # View existiert noch nicht
        sql = render_to_string('%s.sql' % view)
        cursor.execute(sql)


post_syncdb.connect(install_views, sender=sasse_app)
