# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name = "sasse",
    version = "1.0",
    author = "Daniel Steinmann",
    author_email = "dsteinmann@acm.org",
    description = "Unterstützt das Rechnungsbüro der Pontoniere bei der Durchführung eines Wettkampfes.",
    url = "http://code.google.com/p/sasse/",
    packages = [
        "sasse",
        "sasse.migrations",
        "sasse.templatetags",
        "sasse.tests",
    ],
    package_data = {
        'sasse': [
            'templates/*.html',
            'templates/*.sql',
            'templates/registration/*.html',
            'fixtures/*.json',
            'media/*',

        ],
    },
)

