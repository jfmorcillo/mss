# -*- coding: UTF-8 -*-

import os
import locale
import sys
import glob

ADMINS = (('root', 'root@localhost'),)
MANAGERS = ADMINS
PROJECT_DIR = os.path.dirname(__file__)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = "/var/lib/mss/mss-www.db"

TIME_ZONE = 'Europe/Paris'
SITE_ID = 1
USE_I18N = True
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')
MEDIA_URL = '/site_media/'
LOGIN_URL = "/mss/account/login/"

DEFAULT_LANGUAGE = locale.getdefaultlocale()[0]
LANGUAGE_CODE = 'en'
# -*- coding: UTF-8 -*-
#
# (c) 2010 Mandriva, http://www.mandriva.com/
#
# $Id$
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

LANGUAGES = (
  ('en', 'English'),
  ('fr_FR', 'Français'),
)

SECRET_KEY = 'eq*6patei-(m5jat5&s50f#0%(g$plt@q!_n4g!d(^w=f3kgfc'

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
    "mss.www.wizard.context.mes_media",
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',    
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'mss.www.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'wizard', 'templates'),
)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'mss.www.wizard',
    'mss.www.cpserver',
]

for layout in glob.glob(os.path.join(PROJECT_DIR, "layout", "*", "__init__.py")):
    app = 'mss.www.layout.'+layout.split("/")[-2]
    if not app in INSTALLED_APPS:
        INSTALLED_APPS.append(app)

AUTHENTICATION_BACKENDS = (
    'mss.www.backends.MSSBackend',
)

import sys
sys.path.append(os.path.join(PROJECT_DIR, 'lib'))
