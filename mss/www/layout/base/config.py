# -*- coding: UTF-8 -*-
#
# (c) 2010-2012 Mandriva, http://www.mandriva.com/
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

from django.utils.translation import ugettext as _
from mss.www.wizard.config import ConfigManager

config = ConfigManager()

config.add_section({'id': 'core', 'name': _('Core Services')})

config.add_bundle("core", {
    'id': 'users', 'name': _('Users'),
    'icon': 'base/users.png',
    'modules': ["mds_mmc", "mds_smb", "mds_quota"]
})

config.add_bundle("core", {
    'id': 'mail', 'name': _('Mail'),
    'icon': 'base/mail.png',
    'modules': ["mds_mail", "mds_webmail"]
})

config.add_bundle("core", {
    'id': 'net', 'name': _('Network'),
    'icon': 'base/network.png',
    'modules': ["mds_dns", "mds_dhcp"]
})

config.add_bundle("core", {
    'id': 'other', 'name': _('Other'),
    'icon': 'base/other.png',
    'modules': ["mds_cups", "mds_proxy"]
})

config.add_section({'id': 'other', 'name': _('Other Services')})

config.add_bundle("other", {
    'id': 'im', 'name': _('Instant messaging'),
    'icon': 'base/im.png',
    'modules': ["ejabberd"]
})
