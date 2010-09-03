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

class TranslationManager:

    def __init__(self):
        #self.lang = ""
        # set default locale when starting agent
        self.lang = locale.getdefaultlocale()[0]
        self.catalogs = {}

    def set_lang(self, lang):
        self.lang = lang
        for name, infos in self.catalogs.items():
            (path, catalog) = infos
            self.set_catalog(name, path)

    def set_catalog(self, name, path=''):
        try:
            translation = gettext.translation(
                    name,
                    os.path.join(path, "locale"),
                    languages=[self.lang],
                    )
        except AttributeError:
            translation = gettext.NullTranslations()        
        except IOError:
            translation = gettext.NullTranslations()
        self.catalogs[name] = (path, translation)

    def translate(self, string, catalog):
        """Translate a given string to the language of the application."""
        try:
            if self.catalogs[catalog][1] is None:
                return unicode(string)
        except KeyError:
            return unicode(string)
        else:
            return self.catalogs[catalog][1].ugettext(string)    
