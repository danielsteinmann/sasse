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
#            'ENGINE': 'django.db.backends.sqlite3',
#            'NAME': 'db.sqlite',
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'spsv',
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
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'pagination.middleware.PaginationMiddleware',
#    'debug_toolbar.middleware.DebugToolbarMiddleware',
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
#    'debug_toolbar',
)
INTERNAL_IPS = ('127.0.0.1',)

# Have local changes?
try:
    from local_settings import *
except:
    pass