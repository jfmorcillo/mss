# -*- coding: UTF-8 -*-
#
# (c) 2010 Mandriva, http://www.mandriva.com/
#
# $Id: config.py 2233 2010-09-09 08:56:31Z jpbraun $
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

config.add_section({'id': 'partners', 'name': _('Partners'), 'icon': 'mes5/section_partners.png',
    'desc': _('Several appliances from our partners.'), 'conf': {'class': 'block-2'}})

zarafa = {'id': 'zarafa', 'name': _('Zarafa'), 'icon': 'partners/bundle_zarafa.gif',
    'desc': _('Zarafa desc...'), 'modules': ["zarafa"], 'conf': {'class': 'block-2 block-clear'}}

config.add_bundle("partners", zarafa)
config.add_module("mds", "mail", "zarafa")


#    {
#        'id': '1',
#        'name': _('eGroupware Suite'),
#        'icon': 'mes5/bundle_egroupware.png',
#        'desc': _('eGroupware is a enterprise ready groupware software for your network. It enables you to manage contacts, appointments, todos and many more for your whole business. eGroupware is a groupware server. It comes with a native web-interface which allowes to access your data from any platform all over the planet. Moreover you also have the choice to access the EGroupware server with your favorite groupware client (Kontact, Evolution, Outlook) and also with your mobile or PDA via SyncML.'),
#        'modules': ["egroupware"],
#        'conf': {'class': 'block-2 block-clear'},
#    },
#    {
#        'id': '2',
#        'name': _('Group-Office'),
#        'icon': 'mes5/bundle_groupoffice.png',
#        'desc': _('Take your office online. Share projects, calendars, files and e-mail online with co-workers and clients. Easy to use and fully customizable, Group-Office takes online collaboration to the next level.'),
#        'modules': ["groupoffice"],
#        'conf': {'class': 'block-2'},
#    },
#    {
#        'id': '3',
#        'name': _('Authentication Firewall Suite for Linux'),
#        'icon': 'mes5/bundle_nufw.png',
#        'desc': _('NuFW adds user-based filtering to Netfilter, the state of the art IP filtering layer from the Linux kernel. Its exclusive algorithm allows authenticated filtering even on multiuser computers'),
#        'modules': ["nufw"],
#        'conf': {'class': 'block-2 block-clear'},
#    },
