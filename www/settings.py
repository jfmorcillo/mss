# -*- coding: UTF-8 -*-

import os
import locale

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS
PROJECT_DIR = os.path.dirname(__file__)
DEV = True

if DEV:
    DEBUG = True
    TEMPLATE_DEBUG = DEBUG

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = os.path.join(PROJECT_DIR, "mss.db")

TIME_ZONE = 'Europe/Paris'
LANGUAGE_CODE = 'en'
SITE_ID = 1
USE_I18N = True
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')
MEDIA_URL = '/site_media/'
LOGIN_URL = "/mss/login/"

DEFAULT_LANGUAGE = locale.getdefaultlocale()[0]
LANGUAGES = (
  ('en', 'English'),
  ('fr_FR', 'Francais'),
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
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',    
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'www.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'mss',
)
