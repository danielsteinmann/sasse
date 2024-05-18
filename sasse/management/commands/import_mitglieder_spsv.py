# -*- coding: utf-8 -*-

import os
from django.core.management.base import BaseCommand, CommandError
from sasse.eai_mitglieder import handle_file_upload

class Command(BaseCommand):
    help = 'Importiert SPSV Mitglieder Daten aus dem Excel File.'

    def add_arguments(self, parser):
        parser.add_argument("EXCEL-FILE", type=str)

    def handle(self, *args, **options):
        if 'EXCEL-FILE' not in options:
            raise CommandError('Ein Excel File mit Mitgliederdaten als Input erwartet.')
        path = options['EXCEL-FILE']
        if not os.path.isfile(path):
            raise CommandError('%s: Ist kein File.' % path)
        handle_file_upload(path)
        return 0
