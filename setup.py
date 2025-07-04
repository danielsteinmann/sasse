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
            for src in (
                    'manage.py',
                    'mysite/__init__.py',
                    'mysite/settings.py',
                    'mysite/urls.py',
                    'mysite/asgi.py',
                    'mysite/wsgi.py',
                    ):
                dst = "djangosites/wettkaempfe/%s" % src
                myzip.write(src, dst)

setup(
    name = "sasse",
    version = "3.4.2",
    author = "Daniel Steinmann",
    author_email = "dsteinmann@acm.org",
    description = "Unterstützt das Rechnungsbüro der Pontoniere bei der Durchführung eines Wettkampfes.",
    url = "https://github.com/danielsteinmann/sasse",
    packages = find_packages(exclude=['mysite']),
    include_package_data = True,
    install_requires = """
        Django >= 5
        reportlab >= 4
        openpyxl >= 3.1
        psycopg2-binary >= 2.9
        """,
    cmdclass = {
        'sdist': website_sdist,
        }
    )
