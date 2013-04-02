# -*- coding: UTF-8 -*-
#
# (c) 2010-2013 Mandriva, http://www.mandriva.com/
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

import urllib

class Media:

    def __init__(self, module_slug="", slug="", name="", url="", options="", restricted=False, required=False):
        self.module_slug = module_slug
        self.slug = slug
        self.name = name
        self.url = url
        self.options = options.split()
        self.restricted = restricted
        self.required = required

    def get_command(self, login=None, password=None):
        options = []
        url = self.url

        if not u'--distrib' in self.options and not u'--updates' in self.options:
            options.append(self.slug)
        else:
            options = self.options

        if self.restricted:
            assert login
            assert password
            url = url.replace("://", "://%s:%s@" % (urllib.quote(login), urllib.quote(password)), 1)

        return ['urpmi.addmedia'] + options + [ url ]
