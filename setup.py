# -*- coding: utf-8 -*-

# From 'distribute' package
from setuptools import setup, find_packages
from setuptools.command.sdist import sdist

class website_sdist(sdist):
    def run(self):
        sdist.run(self)
        self.wrap_django_site()

    def wrap_django_site(self):
        from zipfile import ZipFile
        with ZipFile("dist/djangosites.zip", "w") as myzip:
            for f in (
                    '__init__.py',
                    'settings.py',
                    'manage.py',
                    'urls.py'
                    ):
                src = "example_project/%s" % f
                dst = "djangosites/wettkaempfe/%s" % f
                myzip.write(src, dst)

setup(
    name = "sasse",
    version = "2.12",
    author = "Daniel Steinmann",
    author_email = "dsteinmann@acm.org",
    description = "Unterstützt das Rechnungsbüro der Pontoniere bei der Durchführung eines Wettkampfes.",
    url = "http://code.google.com/p/sasse/",
    packages = find_packages(exclude=['example_project']),
    include_package_data = True,
    install_requires = """
        django == 1.3
        reportlab == 2.5
        xlrd >= 0.7.1
        South >= 0.7.3
        django-pagination >= 1.0.7
        psycopg2 >= 2.4.1
        """,
    cmdclass = {
        'sdist': website_sdist,
        }
    )
