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

import gettext
import os
import locale
import logging

from mss.agent.lib.utils import Singleton

logger = logging.getLogger(__name__)


class TranslationManager:
    __metaclass__ = Singleton

    def __init__(self):
        # set default locale when starting agent
        self.lang = locale.getdefaultlocale()[0]
        logger.debug("Selected lang: %s" % self.lang)
        self.catalogs = {}

    def set_lang(self, lang):
        self.lang = lang
        for name, infos in self.catalogs.items():
            (path, catalog) = infos
            self.set_catalog(name, path)
        logger.debug("Lang changed to: %s" % self.lang)

    def get_lang(self):
        return self.lang

    def set_catalog(self, name, path=''):
        try:
            translation = gettext.translation(name,
                                              os.path.join(path, "locale"),
                                              languages=[self.lang])
        except AttributeError:
            translation = gettext.NullTranslations()
        except IOError:
            translation = gettext.NullTranslations()
        self.catalogs[name] = (path, translation)

    def get_catalog_path(self, name):
        return self.catalogs[name][0]

    def translate(self, string, catalog):
        """Translate a given string to the language of the application."""
        try:
            if self.catalogs[catalog][1] is None:
                return unicode(string)
        except KeyError:
            return unicode(string)
        else:
            return self.catalogs[catalog][1].ugettext(string)
