# -*- coding: UTF-8 -*-
#
# (c) 2012 Mandriva, http://www.mandriva.com/
#
# This file is part of Mandriva Server Setup
#
# MSS is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MSS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MSS; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import os
import locale
import sys
import glob
import logging
import logging.handlers

logger = logging.getLogger()

ADMINS = (('root', 'root@localhost'),)
MANAGERS = ADMINS
PROJECT_DIR = os.path.dirname(__file__)

DEBUG = False
TEMPLATE_DEBUG = DEBUG

EMAIL_SUBJECT_PREFIX = "[MSS]"
SERVER_EMAIL = "mss+mbs@mandriva.com"

LOG_FILENAME = '/var/log/mss/mss-www.log'
os.chmod(LOG_FILENAME, 0600)

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    LOGGING = {
        'version': 1,
        'handlers': {
            'file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'verbose',
                'filename': LOG_FILENAME
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            }
        },
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            }
        },
        'loggers': {
            'mss': {
                'handlers': ['file', 'console'],
                'level': 'DEBUG',
                'propagate': True
            }
        }
    }
else:
    LOGGING = {
        'version': 1,
        'handlers': {
            'file': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'verbose',
                'filename': LOG_FILENAME
            },
            'console': {
                'level': 'ERROR',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            }
        },
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            }
        },
        'loggers': {
            'mss': {
                'handlers': ['file', 'console'],
                'level': 'ERROR',
                'propagate': True
            }
        }
    }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/var/lib/mss/mss-www.db'
    }
}

TIME_ZONE = 'Europe/Paris'
SITE_ID = 1
USE_I18N = True
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')
MEDIA_URL = '/site_media/'
LOGIN_URL = "/mss/account/login/"

DEFAULT_LANGUAGE = locale.getdefaultlocale()[0]
LANGUAGE_CODE = 'en'

LANGUAGES = (
  ('en', 'English'),
  ('fr_FR', 'Français'),
  ('pt_BR', 'Português do Brasil'),
  ('de_DE', 'Deutsch'),
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.i18n",
    "django.core.context_processors.debug",
    "django.core.context_processors.request",
    "django.core.context_processors.media",
    "mss.www.wizard.context.current_lang"
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'mss.www.errors.middleware.CatchExceptions',
)

ROOT_URLCONF = 'mss.www.urls'

TEMPLATE_DIRS = [
    os.path.join(PROJECT_DIR, 'wizard', 'templates'),
]

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'mss.www.wizard',
    'mss.www.cpserver',
    'mss.www.errors',
]

AUTHENTICATION_BACKENDS = (
    'mss.www.backends.MSSBackend',
)

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# add local python libs in path
if not os.path.abspath(os.path.join(PROJECT_DIR, 'lib')) in sys.path:
    sys.path.append(os.path.abspath(os.path.join(PROJECT_DIR, 'lib')))


TRACEBACK_API_URL = "https://mbs-reports.mandriva.com/api/mss/traceback/"

try:
    from local_settings import *
except ImportError:
    pass
