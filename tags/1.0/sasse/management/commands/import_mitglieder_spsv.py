# -*- coding: utf-8 -*-

import os
from django.core.management.base import BaseCommand, CommandError
from sasse.eai import handle_file_upload

class Command(BaseCommand):
    args = 'excel_file'
    help = 'Importiert SPSV Mitglieder Daten aus dem Excel File.'

    def handle(self, *args, **options):
        if len(args) == 0 or len(args) > 1:
            raise CommandError('Ein Excel File mit Mitgliederdaten als Input erwartet.')
        path = args[0]
        if not os.path.isfile(path):
            raise CommandError('%s: Ist kein File.' % path)
        handle_file_upload(path)
        return 0
