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

import re
import os
from IPy import IP

def get_config_info():
    return ("setup-dns.sh", ["bind_networks", "bind_forwarders"])

def get_current_config():

    bind_networks = []
    if os.path.exists('/var/lib/named/etc/mss_acls.conf'):
        h = open('/var/lib/named/etc/mss_acls.conf')
        f = h.read()
        h.close()
        networks = re.findall('^([\d]{1}.*);$', f, re.MULTILINE)
        for net in networks:
            tmp = IP(net).strNormal(2).split('/')
            if len(tmp) > 1:
                ip = tmp[0]
                mask = tmp[1]
                bind_networks.append((ip, mask))

    bind_forwarders = []
    if os.path.exists('/var/lib/named/etc/mss_forwarders.conf'):
        h = open('/var/lib/named/etc/mss_forwarders.conf')
        f = h.read()
        h.close()
        forwarders = re.findall('^([\d]{1}.*);$', f, re.MULTILINE)
        for forwarder in forwarders:
                bind_forwarders.append(forwarder)

    return {'bind_networks': bind_networks, 'bind_forwarders': bind_forwarders}
