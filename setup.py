# -*- coding: utf-8 -*-

# From 'distribute' package
from setuptools import setup, find_packages

setup(
    name = "sasse",
    version = "1.0",
    author = "Daniel Steinmann",
    author_email = "dsteinmann@acm.org",
    description = "Unterstützt das Rechnungsbüro der Pontoniere bei der Durchführung eines Wettkampfes.",
    url = "http://code.google.com/p/sasse/",
    packages = find_packages(exclude=['example_project']),
    include_package_data = True,
    install_requires = """
        django >= 1.3
        reportlab >= 2.5
        xlrd >= 0.7.1
        South >= 0.7.3
        django-pagination >= 1.0.7
        """,
)

