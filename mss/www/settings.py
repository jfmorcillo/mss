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

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    format = '%(asctime)s|%(name)s|%(levelname)s: %(message)s'
    formatter = logging.Formatter(format)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
else:
    LOG_FILENAME = '/var/log/mss/mss-www.log'
    os.chmod(LOG_FILENAME, 0600)
    fh = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=10485760, backupCount=5)
    fh.setLevel(logging.ERROR)
    logger.addHandler(fh)


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
    "mss.www.wizard.context.current_lang",
    "mss.www.wizard.context.main_media",
    "mss.www.wizard.context.is_mbs",
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'mss.www.better500s.middleware.Better500s',
)

ROOT_URLCONF = 'mss.www.urls'

TEMPLATE_DIRS = [
    os.path.join(PROJECT_DIR, 'wizard', 'templates'),
]

for templates in glob.glob(os.path.join(PROJECT_DIR, "layout", "*", "templates")):
    if os.path.exists(templates):
        TEMPLATE_DIRS.append(templates)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'mss.www.wizard',
    'mss.www.cpserver',
    'mss.www.better500s',
]

for layout in glob.glob(os.path.join(PROJECT_DIR, "layout", "*", "__init__.py")):
    app = 'mss.www.layout.'+layout.split("/")[-2]
    if not app in INSTALLED_APPS:
        INSTALLED_APPS.append(app)

AUTHENTICATION_BACKENDS = (
    'mss.www.backends.MSSBackend',
    'mss.www.backends.MyBackend',
)

# add local python libs in path
if not os.path.abspath(os.path.join(PROJECT_DIR, 'lib')) in sys.path:
    sys.path.append(os.path.abspath(os.path.join(PROJECT_DIR, 'lib')))

BETTER_500_LOG_DIR = os.path.join('/var', 'log', 'mss', '500')
BETTER_500_UNCAUGHT_DIR = ""
BETTER_500_AJAX_URL = "callback/"
BETTER_500_POST_URL = "save/"

try:
    from local_settings import *
except ImportError:
    pass
