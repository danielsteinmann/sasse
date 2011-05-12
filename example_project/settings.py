# Django settings

import os
import sasse

DEBUG = True
TEMPLATE_DEBUG = DEBUG
SASSE_DIR = os.path.dirname(sasse.__file__)

ADMINS = (
    ('Daniel Steinmann', 'dsteinmann@acm.org'),
)

MANAGERS = ADMINS

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'sasse_db.sqlite',
            }
        }

TIME_ZONE = 'Europe/Zurich'
LANGUAGE_CODE = 'de-CH'
SITE_ID = 1
USE_I18N = True
MEDIA_ROOT = os.path.join(SASSE_DIR, 'media')
SECRET_KEY = '_1!)2uy&sz2cx+m#t3r02h_r+q4fal=yu9w8nlal3^zbvcc-z2'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'pagination.middleware.PaginationMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_CONTEXT_PROCESSORS = (
        "django.core.context_processors.auth",
        "django.core.context_processors.debug",
        "django.core.context_processors.i18n",
        "django.core.context_processors.media",
        "django.core.context_processors.request",
        )

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'south',
    'sasse',
    'pagination',
)

# Have local changes?
try:
    from local_settings import *
except:
    pass
